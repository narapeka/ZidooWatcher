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
              <p class="step-description">设置芝杜播放器IP地址，设置BlurayPoster部署的主机IP地址。其余保持默认即可。</p>
            </div>
          </div>

          <div class="step-item">
            <div class="step-number">2</div>
            <div class="step-content">
              <h3 class="step-title">进入配置-路径映射</h3>
              <p class="step-description">添加路径映射，使芝杜播放器开始播放后，获取的源路径能匹配BlurayPoster可识别的路径。</p>
              
              <div class="sub-steps">
                <div class="sub-step">
                  <h4 class="sub-step-title">2.1 如何配置源路径</h4>
                  
                  <div class="sub-sub-step">
                    <h5 class="sub-sub-step-title">方法一：调用芝杜API查看播放后文件的实际路径</h5>
                    <p class="sub-step-description">在芝杜播放器上播放视频，浏览器调用以下地址即可获得芝杜的视频文件源路径</p>
                    <p class="sub-step-description"><code>http://&lt;芝杜IP&gt;:9529/ZidooVideoPlay/getPlayStatus</code></p>
                    <p class="sub-step-description">或者先启动ZidooWatcher服务，芝杜播放器播放视频后，在日志中也可查看芝杜的源路径。</p>
                  </div>

                  <div class="sub-sub-step">
                    <h5 class="sub-sub-step-title">方法二：参照以下转换规则配置源路径</h5>
                    
                    <div class="sub-sub-sub-step">
                      <h6 class="sub-sub-sub-step-title">如果是NFS</h6>
                      <p class="sub-step-description">芝杜海报墙会显示媒体文件为 <code>nfs://ip/myShare/movie/avatar.iso</code></p>
                      <p class="sub-step-description">此处IP后第一个目录myShare实际为NFS一级共享名，后面的/movie/为路径。</p>
                      <p class="sub-step-description">那么源路径应配置为 <code>/mnt/nfs/ip#myShare/movie</code></p>
                      <p class="sub-step-description">（一级目录之前的/要被替换为#，并且前缀nfs://变成/mnt/nfs/）</p>
                    </div>

                    <div class="sub-sub-sub-step">
                      <h6 class="sub-sub-sub-step-title">如果是SMB</h6>
                      <p class="sub-step-description">参照NFS配置，仅需将nfs替换为smb</p>
                    </div>

                    <div class="sub-sub-sub-step">
                      <h6 class="sub-sub-sub-step-title">如果是芝杜内置硬盘或者内置CD2挂载</h6>
                      <p class="sub-step-description">芝杜海报墙会显示媒体文件为 <code>storage:///CloudDrive/115/movie/avatar.iso</code></p>
                      <p class="sub-step-description">那么源路径应填写 <code>/storage/emulated/0/CloudDrive/115/</code></p>
                      <p class="sub-step-description">（storage:///替换为/storage/emulated/0/）</p>
                    </div>
                  </div>
                </div>

                <div class="sub-step">
                  <h4 class="sub-step-title">2.2 如何配置目标路径</h4>
                  <p class="sub-step-description">目标路径可直接配置为蓝光机能识别的路径，参见BlurayPoster项目的说明</p>
                  <p class="sub-step-description">或者可以配置为与BlurayPoster中的Media目录一致，由BlurayPoster再次转译为蓝光机能识别的路径</p>
                  
                  <div class="example">
                    <div class="example-label">示例1：</div>
                    <div class="example-content">
                      <p>ZidooWatcher源路径：<code>/storage/emulated/0/CloudDrive/115/</code></p>
                      <p>ZidooWatcher目标路径：<code>115/</code></p>
                      <p>BlurayPoster Media路径：<code>115/</code></p>
                      <p>BlurayPoster SMB路径：<code>/myNAS/CloudDrive/115</code></p>
                    </div>
                  </div>
                  
                  <div class="example">
                    <div class="example-label">示例2：</div>
                    <div class="example-content">
                      <p>ZidooWatcher源路径：<code>/storage/emulated/0/CloudDrive/115/</code></p>
                      <p>ZidooWatcher目标路径：<code>/myNAS/CloudDrive/115</code></p>
                      <p>（目标路径直接配置为蓝光机可识别，BlurayPoster中无需再次映射）</p>
                    </div>
                  </div>
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
              <div class="step-description">
                <div class="sub-sub-sub-step">
                  <h6 class="sub-sub-sub-step-title">1. 停止服务</h6>
                  <p class="sub-step-description">这会完全停止监控，停止所有拉起操作。</p>
                </div>
                
                <div class="sub-sub-sub-step">
                  <h6 class="sub-sub-sub-step-title">2. 禁用监控目录</h6>
                  <p class="sub-step-description">可单独禁用相关目录的监控，实时生效，无需重启服务。</p>
                </div>
                
                <div class="sub-sub-sub-step">
                  <h6 class="sub-sub-sub-step-title">3. 禁用监控扩展名</h6>
                  <p class="sub-step-description">可单独禁用相关扩展名的监控，实时生效，无需重启服务。</p>
                </div>
              </div>
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
  box-sizing: border-box;
  width: 100%;
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
  width: 3rem;
  height: 3rem;
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  color: white;
  border-radius: 50%;
  font-weight: 800;
  font-size: 1.25rem;
  flex-shrink: 0;
  box-shadow: 0 4px 8px rgba(59, 130, 246, 0.3);
  border: 2px solid rgba(255, 255, 255, 0.1);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.step-content {
  flex: 1;
}

.step-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #ffffff;
  margin: 0 0 0.75rem 0;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
  border-bottom: 2px solid rgba(59, 130, 246, 0.4);
  padding-bottom: 0.5rem;
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
  font-weight: 700;
  color: #f8fafc;
  margin: 0 0 0.75rem 0;
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(59, 130, 246, 0.05));
  padding: 0.75rem 1rem;
  border-radius: 0.5rem;
  border-left: 4px solid #3b82f6;
  text-shadow: 0 1px 1px rgba(0, 0, 0, 0.2);
}

.sub-step-description {
  font-size: 0.95rem;
  color: #cbd5e1;
  line-height: 1.6;
  margin: 0 0 1rem 0;
}

.sub-sub-step {
  margin-top: 1.5rem;
  padding: 1rem;
  background: rgba(15, 23, 42, 0.3);
  border: 1px solid rgba(148, 163, 184, 0.15);
  border-radius: 0.5rem;
  border-left: 3px solid rgba(59, 130, 246, 0.4);
}

.sub-sub-step-title {
  font-size: 1rem;
  font-weight: 600;
  color: #e2e8f0;
  margin: 0 0 0.75rem 0;
  background: rgba(148, 163, 184, 0.1);
  padding: 0.5rem 0.75rem;
  border-radius: 0.375rem;
  border-left: 3px solid #94a3b8;
  font-weight: 600;
}

.sub-sub-sub-step {
  margin-top: 1rem;
  padding: 0.75rem;
  background: rgba(30, 41, 59, 0.2);
  border: 1px solid rgba(148, 163, 184, 0.1);
  border-radius: 0.375rem;
  border-left: 2px solid rgba(148, 163, 184, 0.3);
}

.sub-sub-sub-step-title {
  font-size: 0.95rem;
  font-weight: 600;
  color: #cbd5e1;
  margin: 0 0 0.5rem 0;
  background: rgba(71, 85, 105, 0.1);
  padding: 0.375rem 0.5rem;
  border-radius: 0.25rem;
  border-left: 2px solid #64748b;
  text-transform: uppercase;
  font-size: 0.875rem;
  letter-spacing: 0.05em;
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
  word-wrap: break-word;
  overflow-wrap: break-word;
  max-width: 100%;
  display: inline-block;
  box-sizing: border-box;
}

/* Responsive Design */
@media (max-width: 768px) {
  .help-page {
    padding: 1rem;
    max-width: 100%;
    overflow-x: hidden;
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
    word-wrap: break-word;
    overflow-wrap: break-word;
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
    width: 2.5rem;
    height: 2.5rem;
    font-size: 1.125rem;
  }
  
  .step-title {
    font-size: 1.125rem;
    word-wrap: break-word;
    overflow-wrap: break-word;
  }
  
  .step-description {
    word-wrap: break-word;
    overflow-wrap: break-word;
  }
  
  .sub-step {
    padding: 1rem;
    word-wrap: break-word;
    overflow-wrap: break-word;
  }
  
  .sub-step-title {
    font-size: 1rem;
    word-wrap: break-word;
    overflow-wrap: break-word;
  }
  
  .sub-step-description {
    word-wrap: break-word;
    overflow-wrap: break-word;
  }
  
  .example {
    padding: 0.75rem;
    word-wrap: break-word;
    overflow-wrap: break-word;
  }
  
  code {
    word-break: break-all;
    white-space: pre-wrap;
    overflow-wrap: break-word;
  }
}

@media (max-width: 480px) {
  .help-page {
    padding: 0.75rem;
    max-width: 100%;
    overflow-x: hidden;
  }
  
  .page-title {
    font-size: 1.125rem;
  }
  
  .help-section {
    padding: 1rem;
    word-wrap: break-word;
    overflow-wrap: break-word;
  }
  
  .section-title {
    font-size: 1.125rem;
    margin-bottom: 1rem;
    word-wrap: break-word;
    overflow-wrap: break-word;
  }
  
  .step-item {
    margin-bottom: 1.5rem;
  }
  
  .step-number {
    width: 2rem;
    height: 2rem;
    font-size: 1rem;
    box-shadow: 0 2px 4px rgba(59, 130, 246, 0.3);
  }
  
  .step-title {
    font-size: 1rem;
    word-wrap: break-word;
    overflow-wrap: break-word;
  }
  
  .step-description {
    font-size: 0.9rem;
    word-wrap: break-word;
    overflow-wrap: break-word;
  }
  
  .sub-steps {
    gap: 1rem;
  }
  
  .sub-step {
    padding: 0.75rem;
    word-wrap: break-word;
    overflow-wrap: break-word;
  }
  
  .sub-step-title {
    font-size: 0.95rem;
    word-wrap: break-word;
    overflow-wrap: break-word;
  }
  
  .sub-step-description {
    font-size: 0.875rem;
    word-wrap: break-word;
    overflow-wrap: break-word;
  }
  
  .sub-sub-step {
    padding: 0.75rem;
    word-wrap: break-word;
    overflow-wrap: break-word;
  }
  
  .sub-sub-step-title {
    font-size: 0.9rem;
    word-wrap: break-word;
    overflow-wrap: break-word;
  }
  
  .sub-sub-sub-step {
    padding: 0.5rem;
    word-wrap: break-word;
    overflow-wrap: break-word;
  }
  
  .sub-sub-sub-step-title {
    font-size: 0.85rem;
    word-wrap: break-word;
    overflow-wrap: break-word;
  }
  
  .example {
    padding: 0.5rem;
    word-wrap: break-word;
    overflow-wrap: break-word;
  }
  
  .example-content p {
    font-size: 0.8rem;
    word-wrap: break-word;
    overflow-wrap: break-word;
  }
  
  code {
    font-size: 0.8rem;
    padding: 0.2rem 0.4rem;
    word-break: break-all;
    white-space: pre-wrap;
    overflow-wrap: break-word;
    max-width: 100%;
    display: inline-block;
  }
}
</style> 