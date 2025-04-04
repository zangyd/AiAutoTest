import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'

// 一个简单的Vue组件示例
const MessageComponent = {
  template: '<div>{{ msg }}</div>',
  props: {
    msg: {
      type: String,
      required: true
    }
  }
}

describe('MessageComponent', () => {
  it('renders properly', () => {
    const wrapper = mount(MessageComponent, {
      props: {
        msg: 'Hello Vitest'
      }
    })
    expect(wrapper.text()).toContain('Hello Vitest')
  })
}) 