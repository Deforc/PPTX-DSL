<template>
  <div class="container">
    <h1 class="title">Проверка форматирования презентаций</h1>

    <div class="drop-zone" @dragover="allowDrop" @drop="handlePdfDrop">
      <p v-if="!pdfFile">Перетащите PDF-файл сюда</p>
      <p v-else class="file-name">Загружен: {{ pdfFile.name }}</p>
      <input type="file" accept=".pdf" @change="handlePdfSelect" />
    </div>

    <div class="drop-zone" @dragover="allowDrop" @drop="handleYamlDrop">
      <p v-if="!yamlFile">Перетащите YAML-файл с DSL сюда</p>
      <p v-else class="file-name">Загружен: {{ yamlFile.name }}</p>
      <input type="file" accept=".yaml,.yml" @change="handleYamlSelect" />
    </div>

    <button
      class="validate-btn"
      :disabled="!areFilesReady"
      @click="submitFiles"
    >
      {{ statusText === 'Проверка...' ? 'Проверка...' : 'Запустить проверку' }}
    </button>

    <div class="status-bar" :class="{ 'success': status === 'ok', 'error': status === 'error', 'warning': status === 'warning' }">
      {{ statusText }}
    </div>

  <div class="logs-container">
    <h3>Логи валидации:</h3>
    <div class="logs">
      <div v-for="(line, index) in logLines" :key="index" class="log-line">
        <span class="log-prefix" :class="getLogPrefixClass(line)">{{ splitLogLine(line)[0] }}</span>
        <span class="log-content">{{ splitLogLine(line)[1] }}</span>
      </div>
    </div>
  </div>
  </div>
</template>

<script>
export default {
  name: 'App',
  data() {
    return {
      pdfFile: null,
      yamlFile: null,
      status: '',
      statusText: 'Ожидание файлов...',
      logLines: []
    }
  },
  computed: {
    areFilesReady() {
      return !!this.pdfFile
    }
  },
  methods: {
    allowDrop(e) {
      e.preventDefault()
    },
    handlePdfDrop(e) {
      e.preventDefault()
      const file = e.dataTransfer.files[0]
      if (file && file.type === 'application/pdf') {
        this.pdfFile = file
      } else {
        alert('Пожалуйста, перетащите PDF-файл')
      }
    },
    handlePdfSelect(e) {
      const file = e.target.files[0]
      if (file) {
        this.pdfFile = file
      }
    },
    handleYamlDrop(e) {
      e.preventDefault()
      const file = e.dataTransfer.files[0]
      const ext = file.name.split('.').pop().toLowerCase()
      if (file && (ext === 'yaml' || ext === 'yml')) {
        this.yamlFile = file
      } else {
        alert('Пожалуйста, перетащите YAML-файл')
      }
    },
    handleYamlSelect(e) {
      const file = e.target.files[0]
      if (file) {
        this.yamlFile = file
      }
    },
    getLogPrefixClass(line) {
      if (line.startsWith('[ERROR]')) return 'log-error';
      if (line.startsWith('[WARNING]')) return 'log-warn';
      if (line.startsWith('[INFO]')) return 'log-info';
      if (line.startsWith('[SUCCESS]')) return 'log-success';
      return '';
    },
    
    splitLogLine(line) {
      const match = line.match(/^(\[[A-Z]+\]\s*)(.*)/);
      return match ? [match[1], match[2]] : ['', line];
    },

    async loadDefaultYaml() {
      try {
        const response = await fetch('/example_rules_extended_new.yaml')
        const blob = await response.blob()
        const file = new File([blob], 'example_rules_extended_new.yaml', { type: 'text/yaml' })
        return file
      } catch (err) {
        console.error('Не удалось загрузить стандартные правила', err)
        throw new Error('Не удалось загрузить стандартные правила')
      }
    },

    async submitFiles() {
    if (!this.pdfFile) {
      alert('Загрузите PDF-файл')
      return
    }

    const formData = new FormData()
    formData.append('pdf_file', this.pdfFile)

    let yamlToSend = null

    if (this.yamlFile) {
      yamlToSend = this.yamlFile
    } else {
      try {
        yamlToSend = await this.loadDefaultYaml()
      } catch (err) {
        this.statusText = 'Ошибка загрузки правил'
        this.status = 'error'
        this.logLines = [err.message]
        return
      }
    }

    formData.append('yaml_file', yamlToSend)

    this.status = ''
    this.statusText = 'Проверка...'
    this.logLines = []

    try {
      const response = await fetch('https://pptx-dsl.onrender.com/api/v1/validate', {
        method: 'POST',
        body: formData
      })

      if (response.ok) {
        const result = await response.json()
        if (result.validation) {
          this.statusText = result.status === 'failed' 
            ? 'Проверено. Есть ошибки' 
            : 'Проверено. Ошибок нет'
          this.status = result.status === 'failed' ? 'error' : 'ok'
          this.logLines = result.validation.logs 
        } else {
          this.statusText = result.logs ? 'Проверено. Есть ошибки' : 'Неизвестный формат ответа'
          this.status = 'error'
          this.$refs.logs.textContent = result.logs 
            ? result.logs.join('\n') 
            : JSON.stringify(result, null, 2)
        }
      } else {
        this.statusText = 'Ошибка проверки'
        this.status = 'error'
        this.$refs.logs.textContent = '[ERROR] Не удалось выполнить проверку'
      }
    } catch (err) {
      this.statusText = 'Ошибка подключения'
      this.status = 'error'
      this.$refs.logs.textContent = `[ERROR] ${err.message}`
    }
  },
  }
}
</script>

<style scoped>
.container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background-color: #ffffff; 
  min-height: 100vh; 
  box-sizing: border-box;
}

.title {
  text-align: center;
  color: #1a365d;
  margin-bottom: 30px;
  font-size: 28px;
  font-weight: 700;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.1);
}

.drop-zone {
  border: 2px dashed #3498db;
  border-radius: 12px;
  padding: 40px 20px;
  text-align: center;
  background-color: #ffffff;
  margin-bottom: 24px;
  transition: all 0.3s ease;
  position: relative;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.drop-zone:hover {
  box-shadow: 0 6px 16px rgba(52, 152, 219, 0.18);
  transform: translateY(-2px);
}

.drop-zone input[type="file"] {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  opacity: 0;
  cursor: pointer;
}

.drop-zone p {
  margin: 0;
  color: #2c3e50;
  font-weight: 600;
  font-size: 16px;
}

.status-bar {
  padding: 14px;
  border-radius: 8px;
  text-align: center;
  font-weight: 600;
  margin: 25px 0;
  font-size: 16px;
  letter-spacing: 0.3px;
  color: #1a365d;
}

.status-bar.success {
  background-color: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.status-bar.error {
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.logs-container h3 {
  margin: 0 0 10px 0;
  color: #1a365d; 
  font-size: 18px;
  font-weight: 600;
  text-shadow: 0 1px 1px rgba(0, 0, 0, 0.05);
}

.logs {
  background-color: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 16px;
  height: 220px;
  overflow-y: auto;
  font-family: 'Courier New', monospace;
  font-size: 14px;
  box-shadow: inset 0 2px 10px rgba(0, 0, 0, 0.12);
  line-height: 1.6;
  text-align: left; 
}
.log-line {
  display: flex;
  margin-bottom: 4px;
  font-family: 'Courier New', monospace;
  white-space: pre-wrap;
}

.log-prefix {
  display: inline-block;
  min-width: 85px;
  text-align: left;
  padding-right: 8px;
}

.log-content {
  flex: 1;
  color: #000000;
}

.log-error {
  color: #dc2626;
  font-weight: 600;
}

.log-warn {
  color: #f59e0b;
  font-weight: 600;
}

.log-info {
  color: #3b82f6;
}

.log-success {
  color: #10b981;
  font-weight: 600;
}

.validate-btn {
  display: block;
  margin: 20px auto;
  padding: 12px 24px;
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 6px rgba(52, 152, 219, 0.3);
}

.validate-btn:hover:not(:disabled) {
  background-color: #2980b9;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(52, 152, 219, 0.4);
}

.validate-btn:disabled {
  background-color: #95a5a6;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.validate-btn:focus {
  outline: none;
}
</style>
<style>
body {
  margin: 0;
  padding: 0;
  background-color: #ffffff;
}
</style>
