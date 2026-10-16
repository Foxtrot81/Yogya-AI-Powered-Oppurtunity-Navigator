/**
 * API Client Configuration — Yogya
 *
 * Backend integration boundary connecting the React Native frontend to
 * the FastAPI backend (built by Person 2).
 *
 * Safe-guards & Architecture:
 * - Reads API base URL from EXPO_PUBLIC_API_URL or Constants.expoConfig.extra.apiUrl.
 * - Never hardcodes localhost as the phone's reachable server address.
 * - Detects and warns if localhost/127.0.0.1 is used on native devices (which refers
 *   to the device itself, not the dev machine).
 * - Implements request timeouts using AbortController to avoid hanging on mobile networks.
 * - Clearly marked placeholder endpoints awaiting final OpenAPI contract from Person 2.
 * - Zero secrets or PII included in client requests or error logs.
 */

import Constants from 'expo-constants';
import { Platform } from 'react-native';

// ============================================================================
// BACKEND CONTRACT PLACEHOLDERS (Awaiting Person 2 — FastAPI Team)
// ============================================================================
// These endpoint paths represent standard REST conventions.
// Once Person 2 provides the final OpenAPI / Swagger specification:
// 1. Verify route prefixes (e.g. `/api/v1` vs `/api` vs root `/`)
// 2. Verify query parameter names (e.g. `?type=` vs `?category=`, `?q=` vs `?search=`)
// 3. Confirm response envelope (array vs `{ items: [...] }`)
export const BACKEND_ENDPOINTS = {
  /**
   * GET: Retrieve list of opportunities
   * Expected response: Array of opportunity objects (or { items: [...] })
   * Query params (optional): `type` (scholarship|scheme|training|job), `search` (string)
   */
  OPPORTUNITIES: '/api/v1/opportunities',

  /**
   * GET: Retrieve detailed information for a single opportunity by ID
   * Expected response: Complete Opportunity object including criteria & documents
   */
  OPPORTUNITY_BY_ID: (id: string) => `/api/v1/opportunities/${encodeURIComponent(id)}`,

  /**
   * GET: Health check endpoint to test backend connectivity
   */
  HEALTH: '/api/v1/health',
} as const;

// Default request timeout in milliseconds for mobile network resilience
const DEFAULT_TIMEOUT_MS = 6000;

// Track whether we've already logged the localhost warning to prevent spamming
let hasWarnedLocalhost = false;

/**
 * Custom error class for API errors with HTTP status and endpoint details
 */
export class ApiError extends Error {
  public readonly status?: number;
  public readonly statusText?: string;
  public readonly endpoint: string;

  constructor(message: string, endpoint: string, status?: number, statusText?: string) {
    super(message);
    this.name = 'ApiError';
    this.endpoint = endpoint;
    this.status = status;
    this.statusText = statusText;
  }
}

/**
 * Retrieve the configured backend API base URL from environment variables.
 *
 * Priority:
 * 1. process.env.EXPO_PUBLIC_API_URL (Expo standard convention for SDK 49+)
 * 2. Constants.expoConfig?.extra?.apiUrl (app.json fallback)
 */
export function getApiBaseUrl(): string | null {
  const envUrl = process.env.EXPO_PUBLIC_API_URL?.trim();
  if (envUrl && envUrl !== '__BACKEND_URL_PLACEHOLDER__') {
    return envUrl.replace(/\/+$/, '');
  }

  const extraUrl = (Constants.expoConfig?.extra?.apiUrl as string | undefined)?.trim();
  if (extraUrl && extraUrl !== '__BACKEND_URL_PLACEHOLDER__') {
    return extraUrl.replace(/\/+$/, '');
  }

  return null;
}

/**
 * Check whether a valid, non-placeholder backend base URL has been configured.
 */
export function isBackendConfigured(): boolean {
  return getApiBaseUrl() !== null;
}

/**
 * Inspect the configured URL and warn if localhost is used on a mobile device.
 */
function validateServerUrlForDevice(baseUrl: string): void {
  if (hasWarnedLocalhost) return;

  const isLocalhost = baseUrl.includes('localhost') || baseUrl.includes('127.0.0.1');

  if (isLocalhost && Platform.OS !== 'web') {
    hasWarnedLocalhost = true;
    console.warn(
      'YogyaApi Advisory: EXPO_PUBLIC_API_URL is configured as localhost/127.0.0.1.\n' +
        'On mobile devices (Expo Go), localhost refers to the phone itself rather than your development machine.\n' +
        '• Physical phone: Use your PC LAN IP (e.g. http://192.168.1.X:8000) or an Expo/ngrok tunnel.\n' +
        '• Android emulator: Use http://10.0.2.2:8000.',
    );
  }
}

/**
 * Base fetch wrapper for making HTTP calls to the backend with timeout and error handling.
 *
 * @param endpoint Relative endpoint path (e.g. `/api/v1/opportunities`)
 * @param options Standard RequestInit options (method, headers, body)
 * @param timeoutMs Request timeout before aborting (default 6000ms)
 */
export async function apiFetch<T>(
  endpoint: string,
  options: RequestInit = {},
  timeoutMs: number = DEFAULT_TIMEOUT_MS,
): Promise<T> {
  const baseUrl = getApiBaseUrl();

  if (!baseUrl) {
    throw new ApiError(
      'Backend server URL is not configured. Set EXPO_PUBLIC_API_URL in your .env file.',
      endpoint,
    );
  }

  validateServerUrlForDevice(baseUrl);

  const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  const url = `${baseUrl}${cleanEndpoint}`;

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
      headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      let errorDetail = response.statusText;
      try {
        const errorJson = await response.json();
        if (errorJson && typeof errorJson.detail === 'string') {
          errorDetail = errorJson.detail;
        } else if (errorJson && typeof errorJson.message === 'string') {
          errorDetail = errorJson.message;
        }
      } catch {
        // Ignore JSON parse errors for error bodies
      }

      throw new ApiError(
        `Backend request failed (${response.status}): ${errorDetail}`,
        endpoint,
        response.status,
        response.statusText,
      );
    }

    return (await response.json()) as T;
  } catch (err: any) {
    if (err instanceof ApiError) {
      throw err;
    }

    if (err?.name === 'AbortError') {
      throw new ApiError(
        `Request to backend timed out after ${timeoutMs}ms. Check that the server is reachable.`,
        endpoint,
      );
    }

    throw new ApiError(
      err?.message || 'Network request failed. Ensure FastAPI backend is running and reachable.',
      endpoint,
    );
  } finally {
    clearTimeout(timeoutId);
  }
}
