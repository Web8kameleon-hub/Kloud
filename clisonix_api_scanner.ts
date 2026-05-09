/**
 * 🔍 KLOUD API SCANNER
 * =======================
 * Scanner për zbulimin dhe analizimin e API-ve të Kloud Cloud
 *
 * Ky modul përfshin:
 * - Zbulim automatik i endpoints
 * - Analizë e strukturës së API-ve
 * - Gjenerim i dokumentacionit
 * - Testim i integritetit
 * - Siguri dhe validim
 */

import * as fs from 'fs';
import * as path from 'path';
import * as https from 'https';
import * as http from 'http';
import { URL } from 'url';
import { EventEmitter } from 'events';

interface KloudEndpoint {
    path: string;
    method: string;
    description?: string;
    parameters?: any[];
    responses?: any;
    authenticated?: boolean;
    rateLimited?: boolean;
}

interface KloudAPIScanResult {
    baseUrl: string;
    endpoints: KloudEndpoint[];
    openapi?: any;
    postman?: any;
    timestamp: Date;
    scanDuration: number;
    totalEndpoints: number;
    authenticatedEndpoints: number;
    rateLimitedEndpoints: number;
}

interface ScanConfig {
    baseUrl: string;
    timeout: number;
    maxConcurrency: number;
    includeAuth: boolean;
    authToken?: string;
    userAgent: string;
    followRedirects: boolean;
    maxRedirects: number;
    validateSSL: boolean;
    scanDepth: number;
    excludePatterns: string[];
    includePatterns: string[];
}

class KloudAPIScanner extends EventEmitter {
    private config: ScanConfig;
    private scannedEndpoints: Set<string> = new Set();
    private discoveredEndpoints: KloudEndpoint[] = [];
    private requestQueue: string[] = [];
    private activeRequests: number = 0;
    private startTime: Date = new Date();

    constructor(config: Partial<ScanConfig> = {}) {
        super();

        this.config = {
            baseUrl: config.baseUrl || 'https://api.kloud.cloud',
            timeout: config.timeout || 30000,
            maxConcurrency: config.maxConcurrency || 10,
            includeAuth: config.includeAuth || false,
            authToken: config.authToken,
            userAgent: config.userAgent || 'Kloud-API-Scanner/1.0',
            followRedirects: config.followRedirects || true,
            maxRedirects: config.maxRedirects || 5,
            validateSSL: config.validateSSL || true,
            scanDepth: config.scanDepth || 3,
            excludePatterns: config.excludePatterns || ['/admin', '/debug', '/test'],
            includePatterns: config.includePatterns || ['/api', '/v1', '/v2']
        };
    }

    /**
     * Fillimi i skanimit të plotë të API-së
     */
    async scanAPI(): Promise<KloudAPIScanResult> {
        this.startTime = new Date();
        this.emit('scanStarted', { baseUrl: this.config.baseUrl, timestamp: this.startTime });

        try {
            // Zbulim fillestar i endpoints
            await this.discoverEndpoints();

            // Analizë e detajuar e çdo endpoint
            await this.analyzeEndpoints();

            // Gjenerim i rezultateve
            const result = await this.generateResults();

            this.emit('scanCompleted', result);
            return result;

        } catch (error) {
            this.emit('scanError', error);
            throw error;
        }
    }

    /**
     * Zbulim i endpoints përmes teknika të ndryshme
     */
    private async discoverEndpoints(): Promise<void> {
        this.emit('discoveryStarted');

        // Endpoint bazë për Kloud
        const baseEndpoints = [
            '/api/v1/health',
            '/api/v1/status',
            '/api/v1/info',
            '/api/v1/endpoints',
            '/api/v1/docs',
            '/api/v1/swagger.json',
            '/api/v1/openapi.json',
            '/v1/cycles',
            '/v1/scalability',
            '/v1/intelligence',
            '/v1/asi',
            '/v1/pipelines',
            '/v1/data-sources',
            '/v1/analytics',
            '/v1/billing',
            '/v1/users',
            '/v1/auth',
            '/v1/webhooks',
            '/v1/logs',
            '/v1/metrics'
        ];

        // Shto në queue për analizë
        this.requestQueue.push(...baseEndpoints);

        // Zbulim përmes dokumentacionit
        await this.discoverFromDocumentation();

        // Zbulim përmes spidering
        await this.spiderDiscovery();

        this.emit('discoveryCompleted', { discovered: this.requestQueue.length });
    }

    /**
     * Zbulim nga dokumentacioni i API-së
     */
    private async discoverFromDocumentation(): Promise<void> {
        const docEndpoints = [
            '/api/v1/swagger.json',
            '/api/v1/openapi.json',
            '/api/v1/docs',
            '/docs/api',
            '/swagger',
            '/openapi'
        ];

        for (const endpoint of docEndpoints) {
            try {
                const response = await this.makeRequest(endpoint, 'GET');
                if (response.statusCode === 200) {
                    const docData = JSON.parse(response.data);

                    // Ekstrakt endpoints nga OpenAPI/Swagger
                    if (docData.paths) {
                        for (const [path, methods] of Object.entries(docData.paths)) {
                            for (const [method, details] of Object.entries(methods as any)) {
                                this.addEndpoint({
                                    path: path,
                                    method: method.toUpperCase(),
                                    description: (details as any).description,
                                    parameters: (details as any).parameters,
                                    responses: (details as any).responses
                                });
                            }
                        }
                    }
                }
            } catch (error) {
                // Vazhdo me endpoint tjetër
            }
        }
    }

    /**
     * Zbulim përmes spidering të API-së
     */
    private async spiderDiscovery(): Promise<void> {
        const visited = new Set<string>();
        const toVisit = ['/api/v1', '/v1'];

        for (let depth = 0; depth < this.config.scanDepth; depth++) {
            const currentLevel = [...toVisit];
            toVisit.length = 0;

            for (const endpoint of currentLevel) {
                if (visited.has(endpoint)) continue;
                visited.add(endpoint);

                try {
                    const response = await this.makeRequest(endpoint, 'GET');
                    if (response.statusCode === 200) {
                        // Ekstrakt links nga përgjigja
                        const links = this.extractLinks(response.data);
                        for (const link of links) {
                            if (this.shouldIncludeEndpoint(link)) {
                                toVisit.push(link);
                                this.addEndpoint({ path: link, method: 'GET' });
                            }
                        }
                    }
                } catch (error) {
                    // Vazhdo
                }
            }
        }
    }

    /**
     * Analizë e detajuar e endpoints
     */
    private async analyzeEndpoints(): Promise<void> {
        this.emit('analysisStarted', { total: this.discoveredEndpoints.length });

        // Përpunim paralel me limit concurrency
        const batches = this.chunkArray(this.discoveredEndpoints, this.config.maxConcurrency);

        for (const batch of batches) {
            const promises = batch.map(endpoint => this.analyzeEndpoint(endpoint));
            await Promise.allSettled(promises);
        }

        this.emit('analysisCompleted');
    }

    /**
     * Analizë e një endpoint specifik
     */
    private async analyzeEndpoint(endpoint: KloudEndpoint): Promise<void> {
        const methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD'];

        for (const method of methods) {
            try {
                const response = await this.makeRequest(endpoint.path, method);

                // Analizë e përgjigjes
                endpoint.authenticated = this.checkAuthentication(response);
                endpoint.rateLimited = this.checkRateLimiting(response);

                // Përditëso endpoint
                this.updateEndpoint(endpoint, method, response);

            } catch (error) {
                // Endpoint nuk suporton këtë metodë
            }
        }
    }

    /**
     * Kontroll për autentifikim
     */
    private checkAuthentication(response: any): boolean {
        return response.statusCode === 401 || response.statusCode === 403;
    }

    /**
     * Kontroll për rate limiting
     */
    private checkRateLimiting(response: any): boolean {
        return response.statusCode === 429 ||
               response.headers['x-ratelimit-remaining'] === '0' ||
               response.headers['retry-after'] !== undefined;
    }

    /**
     * Gjenerim i rezultateve përfundimtare
     */
    private async generateResults(): Promise<KloudAPIScanResult> {
        const scanDuration = Date.now() - this.startTime.getTime();

        const result: KloudAPIScanResult = {
            baseUrl: this.config.baseUrl,
            endpoints: this.discoveredEndpoints,
            timestamp: new Date(),
            scanDuration: scanDuration,
            totalEndpoints: this.discoveredEndpoints.length,
            authenticatedEndpoints: this.discoveredEndpoints.filter(e => e.authenticated).length,
            rateLimitedEndpoints: this.discoveredEndpoints.filter(e => e.rateLimited).length
        };

        // Gjenerim OpenAPI spec
        result.openapi = await this.generateOpenAPISpec();

        // Gjenerim Postman collection
        result.postman = await this.generatePostmanCollection();

        return result;
    }

    /**
     * Gjenerim i specifikimit OpenAPI
     */
    private async generateOpenAPISpec(): Promise<any> {
        const spec: any = {
            openapi: '3.0.3',
            info: {
                title: 'Kloud Cloud API',
                version: '1.0.0',
                description: 'API për Kloud Cloud platform'
            },
            servers: [{
                url: this.config.baseUrl,
                description: 'Kloud Cloud API Server'
            }],
            paths: {},
            components: {
                securitySchemes: {
                    bearerAuth: {
                        type: 'http',
                        scheme: 'bearer',
                        bearerFormat: 'JWT'
                    }
                }
            },
            security: [{
                bearerAuth: []
            }]
        };

        // Shto paths
        for (const endpoint of this.discoveredEndpoints) {
            if (!spec.paths[endpoint.path]) {
                spec.paths[endpoint.path] = {};
            }

            spec.paths[endpoint.path][endpoint.method.toLowerCase()] = {
                description: endpoint.description || `Endpoint ${endpoint.method} ${endpoint.path}`,
                parameters: endpoint.parameters || [],
                responses: endpoint.responses || {
                    '200': {
                        description: 'Success'
                    }
                }
            };
        }

        return spec;
    }

    /**
     * Gjenerim i Postman collection
     */
    private async generatePostmanCollection(): Promise<any> {
        const collection: any = {
            info: {
                name: 'Kloud Cloud API',
                description: 'Collection për testimin e Kloud Cloud API',
                schema: 'https://schema.getpostman.com/json/collection/v2.1.0/collection.json'
            },
            item: [],
            variable: [{
                key: 'baseUrl',
                value: this.config.baseUrl,
                type: 'string'
            }]
        };

        // Grupo sipas path
        const groupedEndpoints = this.groupByPath();

        for (const [basePath, endpoints] of Object.entries(groupedEndpoints)) {
            const folder: any = {
                name: basePath,
                item: []
            };

            for (const endpoint of endpoints) {
                folder.item.push({
                    name: `${endpoint.method} ${endpoint.path}`,
                    request: {
                        method: endpoint.method,
                        header: [
                            {
                                key: 'User-Agent',
                                value: this.config.userAgent
                            }
                        ],
                        url: {
                            raw: `{{baseUrl}}${endpoint.path}`,
                            host: ['{{baseUrl}}'],
                            path: endpoint.path.split('/').filter(p => p)
                        }
                    }
                });
            }

            collection.item.push(folder);
        }

        return collection;
    }

    /**
     * Metoda ndihmëse për kërkesa HTTP
     */
    private async makeRequest(endpoint: string, method: string = 'GET'): Promise<any> {
        return new Promise((resolve, reject) => {
            const url = new URL(endpoint, this.config.baseUrl);
            const options: any = {
                hostname: url.hostname,
                port: url.port || (url.protocol === 'https:' ? 443 : 80),
                path: url.pathname + url.search,
                method: method,
                headers: {
                    'User-Agent': this.config.userAgent,
                    'Accept': 'application/json, text/plain, */*'
                },
                timeout: this.config.timeout,
                rejectUnauthorized: this.config.validateSSL
            };

            // Shto auth token nëse është konfiguruar
            if (this.config.includeAuth && this.config.authToken) {
                options.headers['Authorization'] = `Bearer ${this.config.authToken}`;
            }

            const req = (url.protocol === 'https:' ? https : http).request(options, (res) => {
                let data = '';

                res.on('data', (chunk) => {
                    data += chunk;
                });

                res.on('end', () => {
                    resolve({
                        statusCode: res.statusCode,
                        headers: res.headers,
                        data: data
                    });
                });
            });

            req.on('error', (error) => {
                reject(error);
            });

            req.on('timeout', () => {
                req.destroy();
                reject(new Error('Request timeout'));
            });

            req.end();
        });
    }

    /**
     * Metoda ndihmëse për ekstraktimin e links
     */
    private extractLinks(data: string): string[] {
        const links: string[] = [];
        const linkRegex = /href="([^"]*)"/g;
        let match;

        while ((match = linkRegex.exec(data)) !== null) {
            const link = match[1];
            if (link.startsWith('/api') || link.startsWith('/v1')) {
                links.push(link);
            }
        }

        return [...new Set(links)]; // Remove duplicates
    }

    /**
     * Kontroll nëse endpoint duhet të përfshihet
     */
    private shouldIncludeEndpoint(endpoint: string): boolean {
        // Kontrollo exclude patterns
        for (const pattern of this.config.excludePatterns) {
            if (endpoint.includes(pattern)) {
                return false;
            }
        }

        // Kontrollo include patterns
        for (const pattern of this.config.includePatterns) {
            if (endpoint.includes(pattern)) {
                return true;
            }
        }

        return false;
    }

    /**
     * Shto endpoint në listën e zbuluar
     */
    private addEndpoint(endpoint: KloudEndpoint): void {
        const key = `${endpoint.method}:${endpoint.path}`;
        if (!this.scannedEndpoints.has(key)) {
            this.scannedEndpoints.add(key);
            this.discoveredEndpoints.push(endpoint);
        }
    }

    /**
     * Përditëso endpoint me informacione të reja
     */
    private updateEndpoint(endpoint: KloudEndpoint, method: string, response: any): void {
        // Përditëso vetëm nëse është metoda aktuale
        if (endpoint.method === method) {
            // Shto informacione shtesë nga përgjigja
        }
    }

    /**
     * Grupo endpoints sipas path
     */
    private groupByPath(): { [key: string]: KloudEndpoint[] } {
        const groups: { [key: string]: KloudEndpoint[] } = {};

        for (const endpoint of this.discoveredEndpoints) {
            const basePath = endpoint.path.split('/').slice(0, 3).join('/');
            if (!groups[basePath]) {
                groups[basePath] = [];
            }
            groups[basePath].push(endpoint);
        }

        return groups;
    }

    /**
     * Ndaj array në chunks
     */
    private chunkArray<T>(array: T[], size: number): T[][] {
        const chunks: T[][] = [];
        for (let i = 0; i < array.length; i += size) {
            chunks.push(array.slice(i, i + size));
        }
        return chunks;
    }

    /**
     * Ruaj rezultatet në file
     */
    async saveResults(result: KloudAPIScanResult, outputDir: string = './scan-results'): Promise<void> {
        // Krijon direktorinë nëse nuk ekziston
        if (!fs.existsSync(outputDir)) {
            fs.mkdirSync(outputDir, { recursive: true });
        }

        const timestamp = result.timestamp.toISOString().replace(/[:.]/g, '-');

        // Ruaj OpenAPI spec
        if (result.openapi) {
            const openapiPath = path.join(outputDir, `kloud-api-openapi-${timestamp}.json`);
            fs.writeFileSync(openapiPath, JSON.stringify(result.openapi, null, 2));
        }

        // Ruaj Postman collection
        if (result.postman) {
            const postmanPath = path.join(outputDir, `kloud-api-postman-${timestamp}.json`);
            fs.writeFileSync(postmanPath, JSON.stringify(result.postman, null, 2));
        }

        // Ruaj rezultatet e plota
        const resultsPath = path.join(outputDir, `kloud-api-scan-${timestamp}.json`);
        fs.writeFileSync(resultsPath, JSON.stringify(result, null, 2));

        this.emit('resultsSaved', { outputDir, timestamp });
    }
}

/**
 * Funksioni kryesor për skanim
 */
export async function scanKloudAPI(config: Partial<ScanConfig> = {}): Promise<KloudAPIScanResult> {
    const scanner = new KloudAPIScanner(config);

    // Event listeners për monitoring
    scanner.on('scanStarted', (data) => {
        console.log(`🔍 Fillimi i skanimit për ${data.baseUrl}`);
    });

    scanner.on('discoveryCompleted', (data) => {
        console.log(`📋 Zbuluar ${data.discovered} endpoints`);
    });

    scanner.on('analysisCompleted', () => {
        console.log('🔬 Analiza e endpoints përfunduar');
    });

    scanner.on('scanCompleted', (result) => {
        console.log(`✅ Skanimi përfunduar. Koha: ${result.scanDuration}ms`);
        console.log(`📊 Total endpoints: ${result.totalEndpoints}`);
        console.log(`🔐 Authenticated: ${result.authenticatedEndpoints}`);
        console.log(`⏱️  Rate limited: ${result.rateLimitedEndpoints}`);
    });

    scanner.on('scanError', (error) => {
        console.error('❌ Gabim në skanim:', error);
    });

    const result = await scanner.scanAPI();

    // Ruaj rezultatet automatikisht
    await scanner.saveResults(result);

    return result;
}

/**
 * Utility për skanim të shpejtë
 */
export async function quickScan(baseUrl: string): Promise<KloudAPIScanResult> {
    return scanKloudAPI({
        baseUrl,
        timeout: 10000,
        maxConcurrency: 5,
        scanDepth: 2
    });
}

/**
 * Eksportimi i klasës për përdorim të avancuar
 */
export { KloudAPIScanner, KloudEndpoint, KloudAPIScanResult, ScanConfig };

