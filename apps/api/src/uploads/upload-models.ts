/**
 * ðŸš€ Kloud INDUSTRIAL FILE UPLOAD MODELS
 * Production-Grade File Management System
 * Real S3 Integration, Chunked Uploads, Industrial Validation
 */

export interface FileUpload {
  id: string;
  originalName: string;
  filename: string;
  mimetype: string;
  size: number;
  path: string;
  s3Key?: string;
  s3Bucket?: string;
  checksum: string;
  uploadedAt: Date;
  uploadedBy: string;
  status: FileUploadStatus;
  metadata: FileMetadata;
  thumbnailPath?: string;
  processingResults?: ProcessingResults;
}

export interface FileMetadata {
  width?: number;
  height?: number;
  duration?: number;
  format?: string;
  codec?: string;
  bitrate?: number;
  frameRate?: number;
  channels?: number;
  sampleRate?: number;
  tags?: Record<string, any>;
  exif?: Record<string, any>;
  colorSpace?: string;
  compression?: string;
}

export interface ProcessingResults {
  thumbnails: ThumbnailInfo[];
  transcoding?: TranscodingInfo[];
  analysis?: AnalysisResults;
  errors: ProcessingError[];
  completedAt?: Date;
}

export interface ThumbnailInfo {
  size: string; // e.g., "150x150", "300x300", "1920x1080"
  path: string;
  s3Key?: string;
  mimetype: string;
  fileSize: number;
  quality: number;
}

export interface TranscodingInfo {
  format: string;
  quality: string;
  resolution: string;
  path: string;
  s3Key?: string;
  bitrate: number;
  fileSize: number;
  duration: number;
}

export interface AnalysisResults {
  audioLevels?: AudioAnalysis;
  videoQuality?: VideoAnalysis;
  contentDetection?: ContentAnalysis;
  technicalSpecs: TechnicalSpecs;
}

export interface AudioAnalysis {
  peakDb: number;
  rmsDb: number;
  lufsIntegrated: number;
  dynamicRange: number;
  truePeak: number;
  silenceDetection: SilenceSegment[];
}

export interface VideoAnalysis {
  averageBitrate: number;
  frameDrops: number;
  colorRange: string;
  motionVectors: number;
  sceneChanges: number[];
  blackFrames: BlackFrameInfo[];
}

export interface ContentAnalysis {
  faces: FaceDetection[];
  objects: ObjectDetection[];
  text: TextDetection[];
  scenes: SceneDetection[];
  moderation: ModerationResults;
}

export interface SilenceSegment {
  startTime: number;
  endTime: number;
  duration: number;
  threshold: number;
}

export interface BlackFrameInfo {
  frameNumber: number;
  timestamp: number;
  blackPixelRatio: number;
}

export interface FaceDetection {
  boundingBox: BoundingBox;
  confidence: number;
  landmarks?: FaceLandmark[];
  age?: number;
  gender?: string;
  emotion?: string;
}

export interface ObjectDetection {
  class: string;
  confidence: number;
  boundingBox: BoundingBox;
  attributes?: Record<string, any>;
}

export interface TextDetection {
  text: string;
  confidence: number;
  boundingBox: BoundingBox;
  language?: string;
}

export interface SceneDetection {
  startTime: number;
  endTime: number;
  description: string;
  confidence: number;
  tags: string[];
}

export interface ModerationResults {
  adult: number;
  violence: number;
  racy: number;
  medical: number;
  spoof: number;
  likelihood: ModerationLikelihood;
}

export interface BoundingBox {
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface FaceLandmark {
  type: string;
  x: number;
  y: number;
}

export interface TechnicalSpecs {
  fileFormat: string;
  containerFormat: string;
  videoCodec?: string;
  audioCodec?: string;
  resolution?: string;
  frameRate?: number;
  bitDepth?: number;
  colorSpace?: string;
  chromaSubsampling?: string;
  compressionRatio?: number;
}

export interface ProcessingError {
  stage: ProcessingStage;
  error: string;
  timestamp: Date;
  severity: ErrorSeverity;
  details?: Record<string, any>;
}

export enum FileUploadStatus {
  UPLOADING = 'uploading',
  UPLOADED = 'uploaded',
  PROCESSING = 'processing',
  PROCESSED = 'processed',
  FAILED = 'failed',
  DELETED = 'deleted'
}

export enum ProcessingStage {
  UPLOAD = 'upload',
  VALIDATION = 'validation',
  VIRUS_SCAN = 'virus_scan',
  THUMBNAIL = 'thumbnail',
  TRANSCODING = 'transcoding',
  ANALYSIS = 'analysis',
  STORAGE = 'storage',
  CLEANUP = 'cleanup'
}

export enum ErrorSeverity {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  CRITICAL = 'critical'
}

export enum ModerationLikelihood {
  VERY_UNLIKELY = 'very_unlikely',
  UNLIKELY = 'unlikely',
  POSSIBLE = 'possible',
  LIKELY = 'likely',
  VERY_LIKELY = 'very_likely'
}

export interface UploadConfig {
  maxFileSize: number;
  allowedMimeTypes: string[];
  uploadPath: string;
  tempPath: string;
  s3Config: S3Config;
  processingConfig: ProcessingConfig;
  securityConfig: SecurityConfig;
}

export interface S3Config {
  bucket: string;
  region: string;
  accessKeyId: string;
  secretAccessKey: string;
  endpoint?: string;
  forcePathStyle?: boolean;
  signedUrlExpiry: number;
  multipartThreshold: number;
  multipartChunkSize: number;
}

export interface ProcessingConfig {
  enableThumbnails: boolean;
  thumbnailSizes: string[];
  enableTranscoding: boolean;
  transcodingProfiles: TranscodingProfile[];
  enableAnalysis: boolean;
  analysisConfig: AnalysisConfig;
  processingTimeout: number;
  maxConcurrentJobs: number;
}

export interface TranscodingProfile {
  name: string;
  format: string;
  videoCodec?: string;
  audioCodec?: string;
  resolution?: string;
  bitrate?: number;
  quality?: number;
  preset?: string;
}

export interface AnalysisConfig {
  enableAudioAnalysis: boolean;
  enableVideoAnalysis: boolean;
  enableContentDetection: boolean;
  enableModeration: boolean;
  moderationThreshold: number;
  contentDetectionThreshold: number;
}

export interface SecurityConfig {
  enableVirusScan: boolean;
  virusScanTimeout: number;
  allowExecutables: boolean;
  checkFileHeaders: boolean;
  enableContentTypeValidation: boolean;
  maxFilenameLength: number;
  blockedExtensions: string[];
  quarantinePath: string;
}

export interface ChunkUpload {
  uploadId: string;
  chunkNumber: number;
  totalChunks: number;
  chunkSize: number;
  filename: string;
  checksum: string;
  uploadedAt: Date;
}

export interface MultipartUpload {
  uploadId: string;
  filename: string;
  totalSize: number;
  totalChunks: number;
  uploadedChunks: number[];
  s3UploadId?: string;
  createdAt: Date;
  expiresAt: Date;
  completedAt?: Date;
  status: MultipartUploadStatus;
}

export enum MultipartUploadStatus {
  INITIATED = 'initiated',
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed',
  ABORTED = 'aborted',
  EXPIRED = 'expired'
}

export const DEFAULT_UPLOAD_CONFIG: UploadConfig = {
  maxFileSize: 5 * 1024 * 1024 * 1024, // 5GB
  allowedMimeTypes: [
    // Images
    'image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/svg+xml',
    'image/bmp', 'image/tiff', 'image/x-icon', 'image/heic', 'image/heif',
    // Videos
    'video/mp4', 'video/avi', 'video/mov', 'video/wmv', 'video/flv',
    'video/webm', 'video/mkv', 'video/3gp', 'video/m4v', 'video/mts',
    // Audio
    'audio/mp3', 'audio/wav', 'audio/flac', 'audio/aac', 'audio/ogg',
    'audio/m4a', 'audio/wma', 'audio/opus', 'audio/aiff', 'audio/amr',
    // Documents
    'application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/vnd.ms-powerpoint', 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    'text/plain', 'text/csv', 'application/rtf',
    // Archives
    'application/zip', 'application/x-rar-compressed', 'application/x-7z-compressed',
    'application/x-tar', 'application/gzip'
  ],
  uploadPath: '/uploads',
  tempPath: '/tmp/uploads',
  s3Config: {
    bucket: 'Kloud-uploads',
    region: 'eu-central-1',
    accessKeyId: process.env['AWS_ACCESS_KEY_ID'] || '',
    secretAccessKey: process.env['AWS_SECRET_ACCESS_KEY'] || '',
    signedUrlExpiry: 3600, // 1 hour
    multipartThreshold: 100 * 1024 * 1024, // 100MB
    multipartChunkSize: 10 * 1024 * 1024 // 10MB
  },
  processingConfig: {
    enableThumbnails: true,
    thumbnailSizes: ['150x150', '300x300', '600x600', '1200x1200'],
    enableTranscoding: true,
    transcodingProfiles: [
      { name: 'web_high', format: 'mp4', videoCodec: 'h264', audioCodec: 'aac', resolution: '1920x1080', bitrate: 5000, quality: 23 },
      { name: 'web_medium', format: 'mp4', videoCodec: 'h264', audioCodec: 'aac', resolution: '1280x720', bitrate: 2500, quality: 25 },
      { name: 'web_low', format: 'mp4', videoCodec: 'h264', audioCodec: 'aac', resolution: '854x480', bitrate: 1000, quality: 28 },
      { name: 'mobile', format: 'mp4', videoCodec: 'h264', audioCodec: 'aac', resolution: '640x360', bitrate: 500, quality: 30 }
    ],
    enableAnalysis: true,
    analysisConfig: {
      enableAudioAnalysis: true,
      enableVideoAnalysis: true,
      enableContentDetection: true,
      enableModeration: true,
      moderationThreshold: 0.8,
      contentDetectionThreshold: 0.7
    },
    processingTimeout: 3600000, // 1 hour
    maxConcurrentJobs: 10
  },
  securityConfig: {
    enableVirusScan: true,
    virusScanTimeout: 30000, // 30 seconds
    allowExecutables: false,
    checkFileHeaders: true,
    enableContentTypeValidation: true,
    maxFilenameLength: 255,
    blockedExtensions: ['.exe', '.bat', '.cmd', '.com', '.scr', '.pif', '.vbs', '.js', '.jar'],
    quarantinePath: '/quarantine'
  }
};

