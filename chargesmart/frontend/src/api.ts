import axios from 'axios';
import {demoAdapter} from './demo';
export const api=axios.create({baseURL:(import.meta as any).env.VITE_API_URL||'',timeout:120000, ...((import.meta as any).env.VITE_BROWSER_DEMO==='true'?{adapter:demoAdapter}:{})});
export function errorText(e:unknown){return axios.isAxiosError(e)? typeof e.response?.data?.detail==='string'?e.response.data.detail:e.response?.status===422?'Please check your inputs. Battery must exceed reserve.':e.message:e instanceof Error?e.message:'Something went wrong. Please retry.'}
