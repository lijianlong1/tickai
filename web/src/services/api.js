// API 服务文件
// Python 后端：负责数据库 CRUD 和 AI 智能化

const API_BASE_URL = 'http://localhost:8000/api';  // Python 后端

// 通用请求函数
async function request(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  const token = localStorage.getItem('token');

  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  try {
    const response = await fetch(url, {
      ...options,
      headers,
    });

    const data = await response.json();
    console.log('API 响应:', data);

    if (data.code && data.code !== 200) {
      throw new Error(data.message || '请求失败');
    }

    return data;
  } catch (error) {
    console.error('API 请求错误:', error);
    throw error;
  }
}

// ============ 认证相关 ============
export const authApi = {
  register: async (userData) => {
    return request('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  },

  login: async (credentials) => {
    return request('/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    });
  },

  getCurrentUser: async () => {
    return request('/auth/me');
  },
};

// ============ 用户相关 ============
export const userApi = {
  update: (data) => request('/user/update', {
    method: 'PUT',
    body: JSON.stringify(data),
  }),

  recharge: (amount) => request(`/user/recharge?amount=${amount}`, {
    method: 'POST',
  }),

  getBalance: () => request('/user/balance'),

  getRechargeRecords: (params) => {
    const query = new URLSearchParams(params).toString();
    return request(`/user/recharge-records?${query}`);
  },

  getConsumeRecords: (params) => {
    const query = new URLSearchParams(params).toString();
    return request(`/user/consume-records?${query}`);
  },
};

// ============ 社区作品 ============
export const workApi = {
  listPublic: (params) => {
    const query = new URLSearchParams(params).toString();
    return request(`/works?${query}`);
  },

  getDetail: (id) => request(`/works/${id}`),

  create: (data) => request('/works', {
    method: 'POST',
    body: JSON.stringify(data),
  }),

  update: (id, data) => request(`/works/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  }),

  delete: (id) => request(`/works/${id}`, { method: 'DELETE' }),

  like: (id) => request(`/works/${id}/like`, { method: 'POST' }),

  getComments: (id, params) => {
    const query = new URLSearchParams(params).toString();
    return request(`/works/${id}/comments?${query}`);
  },

  addComment: (id, content, parentId = 0) => request(`/works/${id}/comments`, {
    method: 'POST',
    body: JSON.stringify({ content, parent_id: parentId }),
  }),

  favorite: (id) => request(`/works/${id}/favorite`, { method: 'POST' }),
};

// ============ 提示词 ============
export const promptApi = {
  listPublic: (params) => {
    const query = new URLSearchParams(params).toString();
    return request(`/prompts?${query}`);
  },

  getById: (id) => request(`/prompts/${id}`),

  create: (data) => request('/prompts', {
    method: 'POST',
    body: JSON.stringify(data),
  }),

  delete: (id) => request(`/prompts/${id}`, { method: 'DELETE' }),
};

// ============ 创作历史 ============
export const historyApi = {
  list: (params) => {
    const query = new URLSearchParams(params).toString();
    return request(`/create-history?${query}`);
  },

  save: (data) => request('/create-history', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
};

// ============ 语音历史 ============
export const voiceApi = {
  list: (params) => {
    const query = new URLSearchParams(params).toString();
    return request(`/voice-history?${query}`);
  },

  save: (data) => request('/voice-history', {
    method: 'POST',
    body: JSON.stringify(data),
  }),

  delete: (id) => request(`/voice-history/${id}`, { method: 'DELETE' }),
};

// ============ 本地存储工具 ============
export const saveUser = (user, token) => {
  localStorage.setItem('user', JSON.stringify(user));
  localStorage.setItem('token', token);
};

export const getUser = () => {
  const userStr = localStorage.getItem('user');
  return userStr ? JSON.parse(userStr) : null;
};

export const getToken = () => localStorage.getItem('token');

export const clearUser = () => {
  localStorage.removeItem('user');
  localStorage.removeItem('token');
};

export const isAuthenticated = () => !!getToken();

// ============ 视频生成 ============
export const videoApi = {
  // 启动视频生成
  generate: async (params) => {
    return request('/video/generate', {
      method: 'POST',
      body: JSON.stringify(params),
    });
  },

  // 列出我的视频项目
  getProjects: async (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return request(`/video/projects?${query}`);
  },

  // 获取项目详情
  getProject: async (id) => {
    return request(`/video/projects/${id}`);
  },

  // 查询生成状态
  getStatus: async (id) => {
    return request(`/video/projects/${id}/status`);
  },

  // 删除项目
  delete: async (id) => {
    return request(`/video/projects/${id}`, { method: 'DELETE' });
  },

  // 获取下载 URL
  downloadUrl: (id) => {
    return `${API_BASE_URL}/video/projects/${id}/download`;
  },

  // 触发下载
  download: async (id) => {
    const token = getToken();
    const response = await fetch(`${API_BASE_URL}/video/projects/${id}/download`, {
      headers: token ? { 'Authorization': `Bearer ${token}` } : {},
    });
    if (!response.ok) {
      throw new Error('下载失败');
    }
    return response.blob();
  },

  // 获取字幕预设
  getSubtitlePresets: async () => {
    return request('/video/subtitle-presets');
  },

  // 生成字幕预览图
  previewSubtitle: async (text, config) => {
    const query = new URLSearchParams({ text }).toString();
    return request(`/video/preview-subtitle?${query}`, {
      method: 'POST',
      body: JSON.stringify(config),
    });
  },
};

// ============ 模型配置 ============
export const modelConfigApi = {
  // 列出配置
  list: async (type) => {
    const query = type ? new URLSearchParams({ type }).toString() : '';
    return request(`/model-configs${query ? '?' + query : ''}`);
  },

  // 新增配置
  create: async (data) => {
    return request('/model-configs', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  // 更新配置
  update: async (id, data) => {
    return request(`/model-configs/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  // 删除配置
  delete: async (id) => {
    return request(`/model-configs/${id}`, { method: 'DELETE' });
  },

  // 设为默认
  setDefault: async (id) => {
    return request(`/model-configs/${id}/set-default`, { method: 'POST' });
  },

  // 测试连通性
  test: async (id) => {
    return request(`/model-configs/${id}/test`, { method: 'POST' });
  },
};

// ============ 角色管理 ============
export const characterApi = {
  // 列出可见角色
  list: async (keyword) => {
    const query = keyword ? new URLSearchParams({ keyword }).toString() : '';
    return request(`/characters${query ? '?' + query : ''}`);
  },

  // 创建角色
  create: async (data) => {
    return request('/characters', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  // 更新角色
  update: async (id, data) => {
    return request(`/characters/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  // 删除角色
  delete: async (id) => {
    return request(`/characters/${id}`, { method: 'DELETE' });
  },
};

// 导出默认 API 基础 URL（供组件直接构造 URL 使用）
export { API_BASE_URL };
