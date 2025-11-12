<template>
  <div class="container">
    <h1 class="title">Проверка форматирования презентаций</h1>

    <div class="drop-zone" @dragover="allowDrop" @drop="handlePdfDrop">
      <p>Перетащите PDF-файл сюда</p>
      <input type="file" accept=".pdf" @change="handlePdfSelect" />
    </div>

    <div class="drop-zone" @dragover="allowDrop" @drop="handleYamlDrop">
      <p>Перетащите YAML-файл с DSL сюда</p>
      <input type="file" accept=".yaml,.yml" @change="handleYamlSelect" />
    </div>

    <div class="status-bar" :class="{ 'success': status === 'ok', 'error': status === 'error' }">
      {{ statusText }}
    </div>

    <div class="logs-container">
      <h3>Логи валидации:</h3>
      <pre class="logs" ref="logs">
[WARN] Слайд 1: используется 4 шрифта (рекомендуется не более 3)
[ERROR] Слайд 3: цвет текста слишком бледный (контраст ниже нормы)
[INFO] Проверка завершена. Найдено 1 предупреждение, 1 ошибка.
      </pre>
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
      statusText: 'Ожидание файлов...'
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
        this.checkReady()
      } else {
        alert('Пожалуйста, перетащите PDF-файл')
      }
    },
    handlePdfSelect(e) {
      const file = e.target.files[0]
      if (file) {
        this.pdfFile = file
        this.checkReady()
      }
    },
    handleYamlDrop(e) {
      e.preventDefault()
      const file = e.dataTransfer.files[0]
      const ext = file.name.split('.').pop().toLowerCase()
      if (file && (ext === 'yaml' || ext === 'yml')) {
        this.yamlFile = file
        this.checkReady()
      } else {
        alert('Пожалуйста, перетащите YAML-файл')
      }
    },
    handleYamlSelect(e) {
      const file = e.target.files[0]
      if (file) {
        this.yamlFile = file
        this.checkReady()
      }
    },
    checkReady() {
      if (this.pdfFile && this.yamlFile) {
        // Здесь будет вызов API
        setTimeout(() => {
          this.statusText = 'Проверено. Есть ошибки'
          this.status = 'error'
        }, 1000)
      }
    }
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
  color: #2d3748;
  box-shadow: inset 0 2px 10px rgba(0, 0, 0, 0.12);
  white-space: pre-wrap;
  line-height: 1.6;
}
</style>
<style>
body {
  margin: 0;
  padding: 0;
  background-color: #ffffff;
}
</style>
