import { test, expect } from '@playwright/test'

test('basic test', async ({ page }) => {
  // 访问首页
  await page.goto('/')
  
  // 等待页面加载完成
  await page.waitForLoadState('networkidle')
  
  // 验证页面标题
  const title = await page.title()
  expect(title).toBe('自动化测试平台')
  
  // 验证页面 URL
  await expect(page).toHaveURL('/')
  
  // 验证页面内容
  await expect(page.locator('h1')).toBeVisible()
  await expect(page.locator('h1')).toContainText('自动化测试平台')
}) 