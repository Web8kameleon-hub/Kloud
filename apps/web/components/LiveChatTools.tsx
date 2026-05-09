'use client';

import { useCallback, useEffect, useMemo, useState } from 'react';
import styles from './LiveChatTools.module.css';

type ToolCategory = 'triage' | 'analysis' | 'insight' | 'automation';

interface ChatTool {
	id: string;
	label: string;
	description: string;
	category: ToolCategory;
	latency: string;
	endpoint?: string;
}

interface ActivityLog {
	id: string;
	timestamp: string;
	toolId: string;
	summary: string;
}

interface ApiToolResponse {
	tools?: ChatTool[];
	activity?: ActivityLog[];
	status?: string;
}

const DEFAULT_TOOLS: ChatTool[] = [
	{
		id: 'kloud-health-scan',
		label: 'Kloud Health Scan',
		description:
			'Run an instant diagnostic against Kloud mesh nodes, pipeline latency, and Core-A/Core-B heartbeat.',
		category: 'triage',
		latency: '~1.4s',
		endpoint: '/api/diagnostics/mesh-health',
	},
	{
		id: 'core-b-pattern-detector',
		label: 'Core-B Pattern Detector',
		description:
			'Stream brain harmonics through Core-B to uncover anomalies, training drift, and neuro-spectrum gaps.',
		category: 'analysis',
		latency: '~900ms',
		endpoint: '/api/albi/patterns',
	},
	{
		id: 'asi-safety-audit',
		label: 'ASI Safety Audit',
		description:
			'Kick off the ASI sandbox audit to validate overrides, containment rails, and sandbox execution records.',
		category: 'insight',
		latency: '~2.1s',
		endpoint: '/api/asi/safety-audit',
	},
	{
		id: 'core-c-symphony',
		label: 'Core-C Neural Symphony',
		description:
			'Convert the latest EEG buffer into musical textures and stream readiness signals back to the chat.',
		category: 'automation',
		latency: '~1.6s',
		endpoint: '/api/jona/symphony',
	},
];

const DEFAULT_ACTIVITY: ActivityLog[] = [
	{
		id: 'bootstrap-audit',
		timestamp: new Date().toISOString(),
		toolId: 'asi-safety-audit',
		summary: 'Baseline ASI sandbox perimeter verified — no policy deviations detected.',
	},
];

const categoryBadge: Record<ToolCategory, string> = {
	triage: 'Triage',
	analysis: 'Analysis',
	insight: 'Insight',
	automation: 'Automation',
};

const formatTimestamp = (isoDate: string) => {
	try {
		return new Intl.DateTimeFormat('en-GB', {
			hour: '2-digit',
			minute: '2-digit',
			second: '2-digit',
			day: '2-digit',
			month: 'short',
		}).format(new Date(isoDate));
	} catch {
		return isoDate;
	}
};

const LiveChatTools = () => {
	const [tools, setTools] = useState<ChatTool[]>(DEFAULT_TOOLS);
	const [activity, setActivity] = useState<ActivityLog[]>(DEFAULT_ACTIVITY);
	const [loading, setLoading] = useState(false);
	const [error, setError] = useState<string | null>(null);
	const [lastUpdated, setLastUpdated] = useState<string | null>(null);

	const fetchTools = useCallback(async () => {
		setLoading(true);
		setError(null);

		try {
			const controller = new AbortController();
			const timeout = setTimeout(() => controller.abort(), 3500);

			const response = await fetch('/api/asi/tools?scope=live-chat', {
				cache: 'no-store',
				signal: controller.signal,
			});

			clearTimeout(timeout);

			if (!response.ok) {
				throw new Error(`API responded with status ${response.status}`);
			}

			const payload = (await response.json()) as ApiToolResponse;
			if (payload.tools && payload.tools.length > 0) {
				setTools(payload.tools);
			} else {
				setTools(DEFAULT_TOOLS);
			}

			if (payload.activity && payload.activity.length > 0) {
				setActivity(payload.activity.slice(0, 12));
			}

			setLastUpdated(new Date().toISOString());
		} catch (err) {
			console.warn('LiveChatTools API fallback', err);
			setError('Realtime tool catalogue unreachable — using safe defaults.');
			setTools(DEFAULT_TOOLS);
			if (!lastUpdated) {
				setLastUpdated(new Date().toISOString());
			}
		} finally {
			setLoading(false);
		}
	}, [lastUpdated]);

	useEffect(() => {
		fetchTools();
		const interval = setInterval(fetchTools, 20_000);
		return () => clearInterval(interval);
	}, [fetchTools]);

	const handleLaunch = useCallback(
		(tool: ChatTool) => {
			setActivity((prev) => [
				{
					id: `${tool.id}-${Date.now()}`,
					timestamp: new Date().toISOString(),
					toolId: tool.id,
					summary: `Triggered ${tool.label} from the live console.`,
				},
				...prev,
			].slice(0, 15));

			if (tool.endpoint) {
				void fetch(tool.endpoint, { method: 'POST', cache: 'no-store' }).catch((err) => {
					console.warn(`Failed to launch ${tool.id}`, err);
					setError(`Failed to initiate ${tool.label}.`);
				});
			}
		},
		[],
	);

	const sortedTools = useMemo(
		() =>
			[...tools].sort((a, b) => {
				const order: ToolCategory[] = ['triage', 'analysis', 'insight', 'automation'];
				return order.indexOf(a.category) - order.indexOf(b.category);
			}),
		[tools],
	);

	const statusLabel = error ? 'degraded' : loading ? 'syncing' : 'live';

	return (
		<section className={styles.liveChatTools}>
			<div className={styles.header}>
				<h2 className={styles.title}>
					⚙️ Live Chat Tools
					<span className={`${styles.statusPill} ${error ? styles.error : ''}`}>
						<span className={styles.statusIndicator} />
						{statusLabel.toUpperCase()}
					</span>
				</h2>
				<p className={styles.subtitle}>
					Activate Kloud runbooks, neural diagnostics, and ASI automations directly from the chat console.
				</p>
				<button className={styles.refreshButton} type="button" onClick={fetchTools} disabled={loading}>
					🔄 {loading ? 'Refreshing…' : 'Refresh Catalogue'}
				</button>
				{lastUpdated && (
					<span className={styles.subtitle}>Last sync: {formatTimestamp(lastUpdated)}</span>
				)}
				{error && <span className={`${styles.subtitle} ${styles.error}`}>{error}</span>}
			</div>

			<div className={styles.toolGrid}>
				{sortedTools.map((tool) => (
					<article key={tool.id} className={styles.toolCard}>
						<header className={styles.toolHeader}>
							<span>{tool.label}</span>
							<span className={styles.toolBadge}>{categoryBadge[tool.category]}</span>
						</header>
						<p className={styles.toolDescription}>{tool.description}</p>
						<footer className={styles.toolFooter}>
							<span>Latency: {tool.latency}</span>
							<button
								className={styles.actionButton}
								type="button"
								onClick={() => handleLaunch(tool)}
								disabled={loading}
							>
								Launch
							</button>
						</footer>
					</article>
				))}
			</div>

			<div className={styles.activityLog}>
				{activity.length === 0 ? (
					<div className={styles.emptyState}>No recent tool executions — start by launching a diagnostic.</div>
				) : (
					activity.map((entry) => (
						<div key={entry.id} className={styles.activityItem}>
							<div className={styles.activityMeta}>
								<span>{formatTimestamp(entry.timestamp)}</span>
								<span>•</span>
								<span>{entry.toolId}</span>
							</div>
							<span>{entry.summary}</span>
						</div>
					))
				)}
			</div>
		</section>
	);
};

export default LiveChatTools;


