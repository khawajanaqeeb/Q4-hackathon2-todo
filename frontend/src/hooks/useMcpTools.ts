import { useState, useEffect, useCallback } from 'react';
import { InvokeToolResponse, ToolInfo } from '@/types';
import mcpApi from '@/services/mcpApi';

interface UseMcpToolsResult {
  availableTools: ToolInfo[];
  isLoading: boolean;
  error: string | null;
  invokeTool: (toolName: string, parameters: object, provider?: string) => Promise<InvokeToolResponse>;
  refreshAvailableTools: () => Promise<void>;
}

const useMcpTools = (): UseMcpToolsResult => {
  const [availableTools, setAvailableTools] = useState<ToolInfo[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refreshAvailableTools = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await mcpApi.getAvailableTools();
      setAvailableTools(response.tools);
    } catch (err) {
      setError((err as Error).message);
      console.error('Failed to fetch available tools:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Load available tools on mount
  useEffect(() => {
    refreshAvailableTools();
  }, [refreshAvailableTools]);

  const invokeTool = useCallback(async (
    toolName: string,
    parameters: object,
    provider?: string
  ): Promise<InvokeToolResponse> => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await mcpApi.invokeTool(toolName, parameters, provider);
      return response;
    } catch (err) {
      setError((err as Error).message);
      console.error(`Failed to invoke tool ${toolName}:`, err);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  return {
    availableTools,
    isLoading,
    error,
    invokeTool,
    refreshAvailableTools
  };
};

export default useMcpTools;