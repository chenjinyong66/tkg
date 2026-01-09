<template>
  <div class="markdown-editor">
    <div class="editor-toolbar">
      <div class="toolbar-group">
        <a-tooltip title="粗体">
          <a-button size="small" @click="insertMarkdown('**', '**')" class="toolbar-btn">
            <BoldOutlined />
          </a-button>
        </a-tooltip>
        <a-tooltip title="斜体">
          <a-button size="small" @click="insertMarkdown('*', '*')" class="toolbar-btn">
            <ItalicOutlined />
          </a-button>
        </a-tooltip>
        <a-tooltip title="链接">
          <a-button size="small" @click="insertMarkdown('[', '](url)')" class="toolbar-btn">
            <LinkOutlined />
          </a-button>
        </a-tooltip>
        <a-tooltip title="图片">
          <a-button size="small" @click="insertMarkdown('![', '](image_url)')" class="toolbar-btn">
            <PictureOutlined />
          </a-button>
        </a-tooltip>
      </div>
      <div class="toolbar-group">
        <a-tooltip title="标题">
          <a-button size="small" @click="insertMarkdown('# ', '')" class="toolbar-btn">
            <FontColorsOutlined />
          </a-button>
        </a-tooltip>
        <a-tooltip title="列表">
          <a-button size="small" @click="insertMarkdown('- ', '')" class="toolbar-btn">
            <UnorderedListOutlined />
          </a-button>
        </a-tooltip>
        <a-tooltip title="代码">
          <a-button size="small" @click="insertMarkdown('`', '`')" class="toolbar-btn">
            <CodeOutlined />
          </a-button>
        </a-tooltip>
      </div>
      <div class="toolbar-group">
        <a-tooltip title="表格">
          <a-button size="small" @click="insertTable" class="toolbar-btn">
            <TableOutlined />
          </a-button>
        </a-tooltip>
      </div>
    </div>
    <div class="editor-container">
      <textarea
        ref="textareaRef"
        v-model="localValue"
        :placeholder="placeholder"
        class="markdown-textarea"
        @input="handleInput"
        @keydown="handleKeydown"
      ></textarea>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue';
import {
  BoldOutlined,
  ItalicOutlined,
  LinkOutlined,
  PictureOutlined,
  FontColorsOutlined,
  UnorderedListOutlined,
  CodeOutlined,
  TableOutlined
} from '@ant-design/icons-vue';

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  placeholder: {
    type: String,
    default: '输入Markdown内容...'
  }
});

const emit = defineEmits(['update:modelValue', 'change']);

const localValue = ref(props.modelValue);
const textareaRef = ref(null);

// 监听外部值的变化
watch(() => props.modelValue, (newValue) => {
  if (newValue !== localValue.value) {
    localValue.value = newValue;
  }
});

// 监听内部值的变化
watch(localValue, (newValue) => {
  emit('update:modelValue', newValue);
  emit('change', newValue);
});

// 插入Markdown语法
const insertMarkdown = (prefix, suffix) => {
  const textarea = textareaRef.value;
  if (!textarea) return;

  const start = textarea.selectionStart;
  const end = textarea.selectionEnd;
  const selectedText = localValue.value.substring(start, end);
  
  const newContent = localValue.value.substring(0, start) + 
                    prefix + selectedText + suffix + 
                    localValue.value.substring(end);
  
  localValue.value = newContent;
  
  // 设置光标位置
  nextTick(() => {
    const newCursorPos = start + prefix.length + selectedText.length;
    textarea.setSelectionRange(newCursorPos, newCursorPos);
    textarea.focus();
  });
};

// 插入表格
const insertTable = () => {
  const tableMarkdown = '\n| 列1 | 列2 | 列3 |\n| --- | --- | --- |\n| 内容1 | 内容2 | 内容3 |\n';
  insertMarkdown('', tableMarkdown);
};

// 处理输入事件
const handleInput = () => {
  // 不需要额外处理，因为使用了v-model
};

// 处理键盘事件（如Tab键）
const handleKeydown = (event) => {
  if (event.key === 'Tab') {
    event.preventDefault();
    insertMarkdown('    ', ''); // 插入4个空格作为缩进
  }
};

// 暴露方法给父组件
defineExpose({
  focus: () => {
    if (textareaRef.value) {
      textareaRef.value.focus();
    }
  },
  insertText: (text) => {
    const textarea = textareaRef.value;
    if (!textarea) return;

    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    
    const newContent = localValue.value.substring(0, start) + 
                      text + 
                      localValue.value.substring(end);
    
    localValue.value = newContent;
    
    nextTick(() => {
      const newCursorPos = start + text.length;
      textarea.setSelectionRange(newCursorPos, newCursorPos);
      textarea.focus();
    });
  }
});
</script>

<style lang="less" scoped>
.markdown-editor {
  display: flex;
  flex-direction: column;
  border: 1px solid var(--gray-200);
  border-radius: 6px;
  background: var(--gray-0);

  .editor-toolbar {
    display: flex;
    gap: 2px;
    padding: 8px;
    border-bottom: 1px solid var(--gray-200);
    background: var(--gray-25);
    flex-wrap: wrap;

    .toolbar-group {
      display: flex;
      gap: 2px;
      margin-right: 8px;

      .toolbar-btn {
        border: none;
        padding: 4px 8px;
        border-radius: 4px;
        transition: all 0.2s;

        &:hover {
          background: var(--gray-100);
        }
      }
    }
  }

  .editor-container {
    flex: 1;
    display: flex;

    .markdown-textarea {
      flex: 1;
      min-height: 300px;
      padding: 12px;
      border: none;
      resize: none;
      font-family: 'Monaco', 'Consolas', 'Courier New', monospace;
      font-size: 14px;
      line-height: 1.5;
      background: var(--gray-0);
      color: var(--gray-900);

      &:focus {
        outline: none;
      }
    }
  }
}
</style>