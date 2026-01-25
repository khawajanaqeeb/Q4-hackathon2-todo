import axios, { AxiosInstance } from 'axios';
import {
  InvokeToolResponse,
  ToolInfo,
} from '@/types';

const API_BASE_URL = process.env.REACT_APP_MCP_API_URL || '/api/mcp';

class McpApiService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000, // MCP operations might take longer
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add request interceptor for authentication if needed
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('authToken');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        console.error('MCP API Error:', error);
        return Promise.reject(error);
      }
    );
  }

  /**
   * Invoke an MCP tool
   */
  async invokeTool(toolName: string, parameters: object, provider?: string): Promise<InvokeToolResponse> {
    try {
      const response = await this.client.post<InvokeToolResponse>('/tools/invoke', {
        tool_name: toolName,
        parameters,
        provider,
      });
      return response.data;
    } catch (error) {
      throw new Error(`Failed to invoke tool: ${(error as Error).message}`);
    }
  }

  /**
   * Get list of available MCP tools
   */
  async getAvailableTools(): Promise<{ tools: ToolInfo[] }> {
    try {
      const response = await this.client.get<{ tools: ToolInfo[] }>('/tools/available');
      return response.data;
    } catch (error) {
      throw new Error(`Failed to fetch available tools: ${(error as Error).message}`);
    }
  }

  /**
   * Get schema for a specific tool
   */
  async getToolSchema(toolName: string): Promise<any> {
    try {
      const response = await this.client.get(`/tools/schema/${toolName}`);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to fetch tool schema: ${(error as Error).message}`);
    }
  }

  /**
   * Get user activity summary
   */
  async getUserActivity(days: number = 30): Promise<any> {
    try {
      const response = await this.client.get('/user/activity', {
        params: { days },
      });
      return response.data;
    } catch (error) {
      throw new Error(`Failed to fetch user activity: ${(error as Error).message}`);
    }
  }

  /**
   * Get available providers
   */
  async getAvailableProviders(): Promise<{ providers: string[] }> {
    try {
      const response = await this.client.get('/providers/available');
      return response.data;
    } catch (error) {
      throw new Error(`Failed to fetch available providers: ${(error as Error).message}`);
    }
  }
}

export default new McpApiService();