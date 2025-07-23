<template>
  <div class="help-page">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-text">
          <h1 class="page-title">帮助</h1>
        </div>
      </div>
    </div>

    <!-- Help Content -->
    <div class="help-content">
      <div class="section-card">
        <div class="help-section">
          <h2 class="section-title">配置说明</h2>
          
          <div class="step-item">
            <div class="step-number">1</div>
            <div class="step-content">
              <h3 class="step-title">进入配置-系统设置</h3>
              <p class="step-description">设置芝杜播放器IP地址，其余保持默认即可。</p>
            </div>
          </div>

          <div class="step-item">
            <div class="step-number">2</div>
            <div class="step-content">
              <h3 class="step-title">进入配置-路径映射</h3>
              <p class="step-description">添加路径映射，使芝杜播放器开始播放后，获取的源路径能匹配BlurayPoster可识别的路径。</p>
              
              <div class="sub-steps">
                <div class="sub-step">
                  <h4 class="sub-step-title">如果是NFS</h4>
                  <p class="sub-step-description">那么源路径填写 <code>/mnt/nfs/ip#共享名/路径</code>。</p>
                  <div class="example">
                    <div class="example-label">示例：</div>
                    <div class="example-content">
                      <p>芝杜海报墙显示媒体文件为 <code>nfs://192.168.1.50/myShare/movie/avatar.iso</code></p>
                      <p>此处IP后第一个目录myShare实际为一级共享名，后面的/movie/为路径。</p>
                      <p>所以源路径应配置为 <code>/mnt/nfs/192.168.1.50#myShare/movie</code></p>
                    </div>
                  </div>
                </div>

                <div class="sub-step">
                  <h4 class="sub-step-title">如果是SMB</h4>
                  <p class="sub-step-description">参照NFS配置，仅需将nfs替换为smb</p>
                </div>

                <div class="sub-step">
                  <h4 class="sub-step-title">如果是芝杜内置硬盘或者内置CD2挂载</h4>
                  <p class="sub-step-description">那么源路径填写 <code>/storage/emulated/0/路径</code>。</p>
                  <div class="example">
                    <div class="example-label">示例：</div>
                    <div class="example-content">
                      <p>芝杜海报墙显示媒体文件为 <code>storage:///CloudDrive/115/movie/avatar.iso</code></p>
                      <p>此处CloudDrive/115/movie即为路径。</p>
                      <p>所以源路径应配置为 <code>/storage/emulated/0/CloudDrive/115/</code></p>
                    </div>
                  </div>
                </div>

                <div class="sub-step">
                  <h4 class="sub-step-title">其他特殊情况</h4>
                  <p class="sub-step-description">请自行调用芝杜API查看播放后文件的实际路径。</p>
                  <p class="sub-step-description">http://<芝杜IP>:9529/ZidooVideoPlay/getPlayStatus</p>
                  <p class="sub-step-description">或者先启动服务，尝试播放后，在日志中可查看芝杜的实际路径。</p>
                </div>
              </div>
            </div>
          </div>

          <div class="step-item">
            <div class="step-number">3</div>
            <div class="step-content">
              <h3 class="step-title">配置完毕即可启动服务</h3>
              <p class="step-description">同时确保BlurayPosterZidoo特别版也正确配置并启动。</p>
            </div>
          </div>

          <div class="step-item">
            <div class="step-number">4</div>
            <div class="step-content">
              <h3 class="step-title">如果想暂停拉起蓝光机功能</h3>
              <p class="step-description">可以在主页停止服务，或者禁用相关目录的监控。</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// Help page component
</script>

<style scoped>
.help-page {
  padding: 1rem 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 1.5rem;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #ffffff;
  margin: 0;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.help-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.section-card {
  background: rgba(30, 41, 59, 0.8);
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 0.75rem;
  overflow: hidden;
}

.help-section {
  padding: 1.5rem 2rem;
}

.section-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #f1f5f9;
  margin: 0 0 1.5rem 0;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid rgba(148, 163, 184, 0.2);
}

.step-item {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 2.5rem;
  align-items: flex-start;
}

.step-item:last-child {
  margin-bottom: 0;
}

.step-number {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2.5rem;
  height: 2.5rem;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: white;
  border-radius: 50%;
  font-weight: 700;
  font-size: 1.125rem;
  flex-shrink: 0;
}

.step-content {
  flex: 1;
}

.step-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #f1f5f9;
  margin: 0 0 0.75rem 0;
}

.step-description {
  font-size: 1rem;
  color: #cbd5e1;
  line-height: 1.6;
  margin: 0;
}

.sub-steps {
  margin-top: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.sub-step {
  background: rgba(15, 23, 42, 0.4);
  border: 1px solid rgba(148, 163, 184, 0.1);
  border-radius: 0.5rem;
  padding: 1.5rem;
}

.sub-step-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #e2e8f0;
  margin: 0 0 0.75rem 0;
}

.sub-step-description {
  font-size: 0.95rem;
  color: #cbd5e1;
  line-height: 1.6;
  margin: 0 0 1rem 0;
}

.example {
  background: rgba(59, 130, 246, 0.1);
  border: 1px solid rgba(59, 130, 246, 0.2);
  border-radius: 0.375rem;
  padding: 1rem;
}

.example-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: #93c5fd;
  margin-bottom: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.example-content p {
  font-size: 0.9rem;
  color: #e2e8f0;
  line-height: 1.5;
  margin: 0.5rem 0;
}

.example-content p:first-child {
  margin-top: 0;
}

.example-content p:last-child {
  margin-bottom: 0;
}

code {
  font-family: 'SF Mono', 'Monaco', 'Cascadia Code', 'Roboto Mono', 'Consolas', 
    'Menlo', 'DejaVu Sans Mono', 'Liberation Mono', monospace;
  font-size: 0.875rem;
  background: rgba(59, 130, 246, 0.15);
  color: #93c5fd;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  border: 1px solid rgba(59, 130, 246, 0.3);
}

/* Responsive Design */
@media (max-width: 768px) {
  .help-page {
    padding: 1rem;
  }
  
  .page-header {
    text-align: center;
    margin-bottom: 1.5rem;
  }
  
  .page-title {
    font-size: 1.25rem;
  }
  
  .help-section {
    padding: 1.5rem;
  }
  
  .section-title {
    font-size: 1.25rem;
    margin-bottom: 1.5rem;
  }
  
  .step-item {
    flex-direction: column;
    gap: 1rem;
    margin-bottom: 2rem;
  }
  
  .step-number {
    align-self: flex-start;
  }
  
  .step-title {
    font-size: 1.125rem;
  }
  
  .sub-step {
    padding: 1rem;
  }
  
  .sub-step-title {
    font-size: 1rem;
  }
  
  .example {
    padding: 0.75rem;
  }
}

@media (max-width: 480px) {
  .help-page {
    padding: 0.75rem;
  }
  
  .page-title {
    font-size: 1.125rem;
  }
  
  .help-section {
    padding: 1rem;
  }
  
  .section-title {
    font-size: 1.125rem;
    margin-bottom: 1rem;
  }
  
  .step-item {
    margin-bottom: 1.5rem;
  }
  
  .step-number {
    width: 2rem;
    height: 2rem;
    font-size: 1rem;
  }
  
  .step-title {
    font-size: 1rem;
  }
  
  .step-description {
    font-size: 0.9rem;
  }
  
  .sub-steps {
    gap: 1rem;
  }
  
  .sub-step {
    padding: 0.75rem;
  }
  
  .sub-step-title {
    font-size: 0.95rem;
  }
  
  .sub-step-description {
    font-size: 0.875rem;
  }
  
  .example {
    padding: 0.5rem;
  }
  
  .example-content p {
    font-size: 0.8rem;
  }
  
  code {
    font-size: 0.8rem;
    padding: 0.2rem 0.4rem;
  }
}
</style> 