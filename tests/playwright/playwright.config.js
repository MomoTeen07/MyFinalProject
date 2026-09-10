import {defineConfig} from '@playwright/test';
export default defineConfig({testDir:'./tests',use:{baseURL:process.env.BASE_URL||'http://localhost:5174',trace:'on-first-retry'},reporter:'html'});
