import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Shield, 
  Zap, 
  Users, 
  Activity, 
  Server, 
  AlertTriangle, 
  CheckCircle,
  Play,
  Square,
  Cpu,
  Database,
  Lock
} from 'lucide-react';

interface SystemStatus {
  system_id: string;
  running: boolean;
  uptime_seconds: number;
  pulse_balancer: {
    healthy_nodes: number;
    total_nodes: number;
    queue_size: number;
    active_tasks: number;
    statistics: {
      tasks_processed: number;
      crashes_prevented: number;
    };
  };
  security: {
    eu_compliance: boolean;
    encryption_enabled: boolean;
    incidents_count: number;
    security_events: number;
  };
  performance: {
    total_operations: number;
    distributed_tasks: number;
    pulses_sent: number;
    crashes_prevented: number;
  };
}

interface PulseData {
  timestamp: string;
  node_id: string;
  pulse_id: string;
  message: string;
}

export default function KloudDemo() {
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [pulseLog, setPulseLog] = useState<PulseData[]>([]);
  const [logs, setLogs] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);

  // Mock system status for demo
  const mockSystemStatus: SystemStatus = {
    system_id: 'Kloud-demo-' + Math.random().toString(36).substr(2, 8),
    running: isRunning,
    uptime_seconds: isRunning ? Math.floor(Date.now() / 1000) % 3600 : 0,
    pulse_balancer: {
      healthy_nodes: 3,
      total_nodes: 3,
      queue_size: 0,
      active_tasks: isRunning ? Math.floor(Math.random() * 3) : 0,
      statistics: {
        tasks_processed: isRunning ? Math.floor(Math.random() * 50) + 10 : 0,
        crashes_prevented: 0
      }
    },
    security: {
      eu_compliance: true,
      encryption_enabled: true,
      incidents_count: 0,
      security_events: isRunning ? Math.floor(Math.random() * 20) + 5 : 0
    },
    performance: {
      total_operations: isRunning ? Math.floor(Math.random() * 100) + 50 : 0,
      distributed_tasks: isRunning ? Math.floor(Math.random() * 30) + 10 : 0,
      pulses_sent: isRunning ? Math.floor((Date.now() / 1000) % 3600) * 3 : 0,
      crashes_prevented: 0
    }
  };

  // Simulate real-time updates
  useEffect(() => {
    let interval: NodeJS.Timeout;
    
    if (isRunning) {
      interval = setInterval(() => {
        setSystemStatus(prev => prev ? {
          ...prev,
          uptime_seconds: prev.uptime_seconds + 1,
          performance: {
            ...prev.performance,
            pulses_sent: prev.performance.pulses_sent + 3 // 3 nodes × 1 pulse per second
          }
        } : mockSystemStatus);

        // Add pulse log entries
        const nodes = ['secure-node-1', 'secure-node-2', 'secure-node-3'];
        nodes.forEach(nodeId => {
          setPulseLog(prev => {
            const newPulse: PulseData = {
              timestamp: new Date().toLocaleTimeString(),
              node_id: nodeId,
              pulse_id: Math.random().toString(36).substr(2, 8),
              message: `💓 Pulse from ${nodeId}`
            };
            return [newPulse, ...prev.slice(0, 19)]; // Keep last 20 entries
          });
        });

        // Add system logs
        const logMessages = [
          '✅ Task completed successfully',
          '💓 System pulse healthy', 
          '🔒 Security check passed',
          '⚖️ Load balancing active',
          '📊 Performance metrics updated'
        ];
        
        if (Math.random() > 0.7) {
          setLogs(prev => [
            `${new Date().toLocaleTimeString()} - ${logMessages[Math.floor(Math.random() * logMessages.length)]}`,
            ...prev.slice(0, 9)
          ]);
        }
      }, 1000);
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isRunning]);

  const startSystem = async () => {
    setLoading(true);
    setLogs(['🚀 Starting Kloud Integrated System...']);
    
    // Simulate startup sequence
    setTimeout(() => {
      setLogs(prev => [...prev, '✅ EU Security System initialized']);
    }, 500);
    
    setTimeout(() => {
      setLogs(prev => [...prev, '💓 Pulse Balancer started (1.0s interval)']);
    }, 1000);
    
    setTimeout(() => {
      setLogs(prev => [...prev, '🔐 Secure nodes registered']);
    }, 1500);
    
    setTimeout(() => {
      setLogs(prev => [...prev, '✅ System ready for operation']);
      setIsRunning(true);
      setSystemStatus(mockSystemStatus);
      setLoading(false);
    }, 2000);
  };

  const stopSystem = () => {
    setIsRunning(false);
    setSystemStatus(null);
    setPulseLog([]);
    setLogs(['🛑 System stopped successfully']);
  };

  const formatUptime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}m ${secs}s`;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-neutral-900 via-neutral-900 to-neutral-900 text-white p-6">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-violet-400 to-violet-300 bg-clip-text text-transparent">
              Kloud Integrated System
            </h1>
            <p className="text-slate-300 mt-2">
              EU-Compliant Security • Pulse-Based Load Balancing • Crash Prevention
            </p>
          </div>
          
          <div className="flex gap-4">
            <Button 
              onClick={startSystem} 
              disabled={isRunning || loading}
              className="bg-green-600 hover:bg-green-700"
            >
              <Play className="w-4 h-4 mr-2" />
              {loading ? 'Starting...' : 'Start Demo'}
            </Button>
            
            <Button 
              onClick={stopSystem} 
              disabled={!isRunning}
              variant="destructive"
            >
              <Square className="w-4 h-4 mr-2" />
              Stop Demo
            </Button>
          </div>
        </div>
      </div>

      {/* System Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <Card className="bg-neutral-800/50 border-neutral-700">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-slate-300 flex items-center">
              <Shield className="w-4 h-4 mr-2 text-green-400" />
              EU Security
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-400">
              {systemStatus?.security.eu_compliance ? 'COMPLIANT' : 'OFFLINE'}
            </div>
            <div className="text-xs text-neutral-400 mt-1">
              GDPR • NIS2 • Encryption
            </div>
          </CardContent>
        </Card>

        <Card className="bg-neutral-800/50 border-neutral-700">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-slate-300 flex items-center">
              <Zap className="w-4 h-4 mr-2 text-yellow-400" />
              Pulse System
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-400">
              {systemStatus ? `${systemStatus.performance.pulses_sent}` : '0'}
            </div>
            <div className="text-xs text-neutral-400 mt-1">
              Total Pulses (1.0s interval)
            </div>
          </CardContent>
        </Card>

        <Card className="bg-neutral-800/50 border-neutral-700">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-slate-300 flex items-center">
              <Users className="w-4 h-4 mr-2 text-violet-400" />
              Active Nodes
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-violet-400">
              {systemStatus ? `${systemStatus.pulse_balancer.healthy_nodes}/${systemStatus.pulse_balancer.total_nodes}` : '0/0'}
            </div>
            <div className="text-xs text-neutral-400 mt-1">
              Healthy/Total
            </div>
          </CardContent>
        </Card>

        <Card className="bg-neutral-800/50 border-neutral-700">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-slate-300 flex items-center">
              <Activity className="w-4 h-4 mr-2 text-purple-400" />
              Tasks Processed
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-purple-400">
              {systemStatus?.pulse_balancer.statistics.tasks_processed || 0}
            </div>
            <div className="text-xs text-neutral-400 mt-1">
              Distributed Processing
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* System Status */}
        <Card className="bg-neutral-800/50 border-neutral-700">
          <CardHeader>
            <CardTitle className="flex items-center">
              <Server className="w-5 h-5 mr-2" />
              System Status
            </CardTitle>
          </CardHeader>
          <CardContent>
            {systemStatus ? (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-slate-300">System ID:</span>
                  <Badge variant="outline" className="font-mono text-xs">
                    {systemStatus.system_id}
                  </Badge>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-slate-300">Status:</span>
                  <Badge className="bg-green-600">
                    <CheckCircle className="w-3 h-3 mr-1" />
                    Running
                  </Badge>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-slate-300">Uptime:</span>
                  <span className="font-mono text-green-400">
                    {formatUptime(systemStatus.uptime_seconds)}
                  </span>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-slate-300">Queue Size:</span>
                  <span className="font-mono text-violet-400">
                    {systemStatus.pulse_balancer.queue_size}
                  </span>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-slate-300">Active Tasks:</span>
                  <span className="font-mono text-purple-400">
                    {systemStatus.pulse_balancer.active_tasks}
                  </span>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-slate-300">Security Events:</span>
                  <span className="font-mono text-yellow-400">
                    {systemStatus.security.security_events}
                  </span>
                </div>
              </div>
            ) : (
              <div className="text-center py-8 text-neutral-400">
                <Server className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p>System offline</p>
                <p className="text-sm">Click &quot;Start Demo&quot; to begin</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Real-time Pulse Log */}
        <Card className="bg-neutral-800/50 border-neutral-700">
          <CardHeader>
            <CardTitle className="flex items-center">
              <Activity className="w-5 h-5 mr-2" />
              Live Pulse Log
              <Badge className="ml-2 bg-green-600/20 text-green-400">
                {isRunning ? 'LIVE' : 'OFFLINE'}
              </Badge>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64 overflow-y-auto space-y-1">
              {pulseLog.map((pulse, index) => (
                <div 
                  key={index} 
                  className="text-xs font-mono p-2 bg-neutral-900/50 rounded border border-neutral-700"
                >
                  <span className="text-neutral-400">[{pulse.timestamp}]</span>
                  <span className="text-violet-400 ml-2">{pulse.node_id}</span>
                  <span className="text-slate-300 ml-2">{pulse.message}</span>
                </div>
              ))}
              {pulseLog.length === 0 && (
                <div className="text-center py-8 text-neutral-400">
                  <Activity className="w-8 h-8 mx-auto mb-2 opacity-50" />
                  <p>No pulse activity</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* System Logs */}
        <Card className="bg-neutral-800/50 border-neutral-700 lg:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center">
              <Database className="w-5 h-5 mr-2" />
              System Logs
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-48 overflow-y-auto space-y-1">
              {logs.map((log, index) => (
                <div 
                  key={index} 
                  className="text-sm font-mono p-2 bg-neutral-900/30 rounded"
                >
                  {log}
                </div>
              ))}
              {logs.length === 0 && (
                <div className="text-center py-8 text-neutral-400">
                  <Database className="w-8 h-8 mx-auto mb-2 opacity-50" />
                  <p>No logs available</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Security Compliance Badge */}
      <div className="mt-8 flex justify-center">
        <Alert className="bg-green-900/20 border-green-600 max-w-md">
          <Lock className="h-4 w-4" />
          <AlertDescription className="text-green-300">
            <strong>EU Compliant:</strong> GDPR, NIS2, AES-256 Encryption, DDoS Protection
          </AlertDescription>
        </Alert>
      </div>
    </div>
  );
}


