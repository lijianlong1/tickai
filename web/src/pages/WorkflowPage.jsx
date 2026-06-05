import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import Navbar from '../components/Navbar';
import AgentStageCard from '../components/workflow/AgentStageCard';
import TimelineEditor from '../components/workflow/TimelineEditor';
import { workflowApi } from '../services/api';
import { useUser } from '../contexts/UserContext';

// 5 个智能体的元数据
const AGENTS = [
  {
    name: 'storyboarder',
    display_name: '分镜师',
    description: '将原始需求拆分为结构化的分镜剧本',
    icon: '🎬',
    color: '#6366F1',
  },
  {
    name: 'illustrator',
    display_name: '画师',
    description: '为主体和背景分别生成图像',
    icon: '🎨',
    color: '#EC4899',
  },
  {
    name: 'scriptwriter',
    display_name: '编剧',
    description: '基于图像内容撰写情感匹配的旁白',
    icon: '✍️',
    color: '#8B5CF6',
  },
  {
    name: 'voice_actor',
    display_name: '配音师',
    description: '将旁白转为语音',
    icon: '🎙️',
    color: '#06B6D4',
  },
  {
    name: 'editor',
    display_name: '剪辑师',
    description: '合成图像和音频为最终视频',
    icon: '🎞️',
    color: '#F59E0B',
  },
];

// 阶段状态映射
const STAGE_AGENT_MAP = {
  init: null,
  storyboard: 'storyboarder',
  illustrate: 'illustrator',
  script: 'scriptwriter',
  voice: 'voice_actor',
  editing: 'editor',
  completed: null,
  failed: null,
};

function WorkflowPage() {
  const navigate = useNavigate();
  const { id } = useParams();
  const { user } = useUser();

  const [phase, setPhase] = useState(id ? 'run' : 'config'); // config / run / edit
  const [workflowId, setWorkflowId] = useState(id ? parseInt(id) : null);
  const [workflow, setWorkflow] = useState(null);
  const [isStarting, setIsStarting] = useState(false);
  const [error, setError] = useState('');

  // 配置表单
  const [formData, setFormData] = useState({
    title: '',
    original_prompt: '',
    panel_count: 6,
    ratio: '16:9',
    duration: 30,
    model_config: {
      storyboard: { provider: 'minimax', model: 'minimax-text-01' },
      subject_image: { provider: 'minimax', model: 'minimax-image-01' },
      background_image: { provider: 'minimax', model: 'minimax-image-01' },
      vision: { provider: 'minimax', model: 'minimax-vl-01' },
      narration: { provider: 'minimax', model: 'minimax-text-01' },
      voice: { provider: 'openai', model: 'tts-1', voice: 'alloy' },
    },
    subtitle_config: {
      enabled: true,
      position: 'bottom_center',
      font_size: 48,
      font_color: '#FFFFFF',
      outline_color: '#000000',
      outline_width: 2,
      bold: true,
      bg_enabled: true,
      bg_color: '#00000080',
    },
  });

  const pollRef = useRef(null);

  // 加载工作流状态
  useEffect(() => {
    if (workflowId) {
      loadWorkflowState();
      // 启动轮询
      pollRef.current = setInterval(loadWorkflowState, 2000);
    }
    return () => {
      if (pollRef.current) clearInterval(pollRef.current);
    };
  }, [workflowId]);

  const loadWorkflowState = async () => {
    if (!workflowId) return;
    try {
      const response = await workflowApi.getState(workflowId);
      setWorkflow(response.data);
      // 如果完成，切换到编辑阶段
      if (response.data.current_stage === 'completed') {
        // 保留在 run 阶段，但显示编辑按钮
      }
    } catch (err) {
      console.error('加载工作流状态失败:', err);
    }
  };

  // 启动工作流
  const handleStart = async () => {
    if (!user) {
      alert('请先登录');
      return;
    }
    if (formData.original_prompt.length < 10) {
      setError('原始需求至少需要 10 个字');
      return;
    }

    setIsStarting(true);
    setError('');
    try {
      const response = await workflowApi.start(formData);
      setWorkflowId(response.data.workflow_id);
      setPhase('run');
    } catch (err) {
      setError(err.message || '启动失败');
    } finally {
      setIsStarting(false);
    }
  };

  // 重做某个智能体
  const handleRegenerateStage = async (agentName) => {
    if (!confirm(`确定要重新执行 ${AGENTS.find(a => a.name === agentName)?.display_name} 吗？`)) return;
    try {
      // 这里需要后端提供重做某个阶段的接口
      alert('重做功能开发中，请稍后重试');
    } catch (err) {
      alert('重做失败: ' + err.message);
    }
  };

  // 重新合成
  const handleRecompose = async () => {
    try {
      const response = await workflowApi.recompose(workflowId);
      if (response.code === 200) {
        alert('重新合成成功！');
        loadWorkflowState();
      }
    } catch (err) {
      alert('合成失败: ' + err.message);
    }
  };

  // 计算每个智能体的状态
  const getAgentState = (agentName) => {
    if (!workflow) return { status: 'pending', progress: 0, message: '等待中' };
    const currentStage = workflow.current_stage;
    const currentAgent = STAGE_AGENT_MAP[currentStage];

    if (currentStage === 'failed' || currentStage === 'init') {
      return { status: 'pending', progress: 0, message: '等待中' };
    }
    if (currentAgent === agentName) {
      return { status: 'running', progress: workflow.progress, message: workflow.current_step || '执行中...' };
    }

    // 检查智能体是否已完成
    const stageOrder = ['storyboarder', 'illustrator', 'scriptwriter', 'voice_actor', 'editor'];
    const currentIdx = stageOrder.indexOf(currentAgent);
    const agentIdx = stageOrder.indexOf(agentName);
    if (currentIdx > agentIdx || currentStage === 'completed') {
      return { status: 'success', progress: 100, message: '已完成' };
    }
    return { status: 'pending', progress: 0, message: '等待中' };
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-purple-50">
      <Navbar />

      <div className="container mx-auto px-6 pt-24 pb-12">
        {/* 头部 */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center px-4 py-2 rounded-full bg-gradient-to-r from-blue-100 to-purple-100 border border-blue-200 text-blue-700 text-sm font-medium mb-4">
            <span className="w-2 h-2 bg-blue-500 rounded-full mr-2 animate-pulse"></span>
            AI 智能体工作流
          </div>
          <h1 className="text-4xl font-black mb-3">
            <span className="bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">
              多智能体协作创作视频
            </span>
          </h1>
          <p className="text-base text-gray-600 max-w-2xl mx-auto">
            5 个 AI 智能体依次工作：分镜师 → 画师 → 编剧 → 配音师 → 剪辑师
          </p>
        </div>

        {/* ============ 配置阶段 ============ */}
        {phase === 'config' && (
          <div className="max-w-3xl mx-auto">
            <div className="bg-white/80 backdrop-blur-sm rounded-3xl shadow-2xl p-8 border border-gray-100">
              {error && (
                <div className="mb-6 p-4 rounded-xl bg-red-50 border border-red-200 text-red-700 text-sm">
                  {error}
                </div>
              )}

              <div className="space-y-6">
                {/* 标题 */}
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    视频标题
                  </label>
                  <input
                    type="text"
                    value={formData.title}
                    onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                    className="w-full px-5 py-3 rounded-xl border-2 border-gray-200 focus:border-blue-500 focus:ring-4 focus:ring-blue-100 outline-none"
                    placeholder="给你的视频起个名字"
                    required
                  />
                </div>

                {/* 镜头数 */}
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <label className="text-sm font-semibold text-gray-700">
                      镜头数量
                    </label>
                    <span className="text-2xl font-black text-blue-600">
                      {formData.panel_count}
                    </span>
                  </div>
                  <input
                    type="range"
                    min="2"
                    max="12"
                    value={formData.panel_count}
                    onChange={(e) => setFormData({ ...formData, panel_count: parseInt(e.target.value) })}
                    className="w-full"
                  />
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>2 个</span>
                    <span>6 个（推荐）</span>
                    <span>12 个</span>
                  </div>
                </div>

                {/* 比例 */}
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    画面比例
                  </label>
                  <div className="grid grid-cols-4 gap-2">
                    {[
                      { value: '16:9', label: '16:9' },
                      { value: '9:16', label: '9:16' },
                      { value: '1:1', label: '1:1' },
                      { value: '4:3', label: '4:3' },
                    ].map((opt) => (
                      <button
                        key={opt.value}
                        type="button"
                        onClick={() => setFormData({ ...formData, ratio: opt.value })}
                        className={`py-2.5 rounded-lg border-2 font-medium text-sm transition-all ${
                          formData.ratio === opt.value
                            ? 'border-blue-500 bg-blue-50 text-blue-700'
                            : 'border-gray-200 hover:border-gray-300 text-gray-700'
                        }`}
                      >
                        {opt.label}
                      </button>
                    ))}
                  </div>
                </div>

                {/* 原始需求 */}
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    你的创作需求
                  </label>
                  <textarea
                    rows={4}
                    value={formData.original_prompt}
                    onChange={(e) => setFormData({ ...formData, original_prompt: e.target.value })}
                    className="w-full px-5 py-3 rounded-xl border-2 border-gray-200 focus:border-blue-500 focus:ring-4 focus:ring-blue-100 outline-none resize-none"
                    placeholder="例如：一个小英雄在森林里冒险，遇到了一只会说话的狐狸，它们一起踏上了寻找魔法石的道路..."
                    minLength={10}
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    至少 10 个字，描述越详细 AI 创作效果越好
                  </p>
                </div>

                {/* 启动按钮 */}
                <button
                  onClick={handleStart}
                  disabled={isStarting || !user || (user.balance || 0) < 5}
                  className="w-full relative group overflow-hidden px-8 py-4 rounded-xl font-semibold text-white transition-all duration-300 hover:scale-[1.02] disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <div className="absolute inset-0 bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600"></div>
                  <div className="absolute inset-0 bg-gradient-to-r from-blue-700 via-purple-700 to-pink-700 opacity-0 group-hover:opacity-100 transition-opacity"></div>
                  <span className="relative flex items-center justify-center">
                    {isStarting ? '启动中...' :
                     !user ? '请先登录' :
                     (user.balance || 0) < 5 ? '余额不足（至少 5 元）' :
                     '🚀 启动智能体工作流'}
                  </span>
                </button>
              </div>
            </div>
          </div>
        )}

        {/* ============ 执行阶段 ============ */}
        {phase === 'run' && workflowId && workflow && (
          <div className="max-w-5xl mx-auto">
            {/* 顶部进度条 */}
            <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg p-5 mb-6 border border-gray-100">
              <div className="flex items-center justify-between mb-3">
                <div>
                  <h2 className="text-lg font-bold text-gray-900">{workflow.title}</h2>
                  <p className="text-xs text-gray-500 mt-0.5">
                    {workflow.current_step || '准备中...'}
                  </p>
                </div>
                <span className="text-2xl font-black text-blue-600">
                  {workflow.progress}%
                </span>
              </div>
              <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                <div
                  className="h-full transition-all duration-500 rounded-full bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500"
                  style={{ width: `${workflow.progress}%` }}
                />
              </div>
            </div>

            {/* 智能体阶段卡片（5 个） */}
            <div className="space-y-3 mb-6">
              {AGENTS.map((agent) => (
                <AgentStageCard
                  key={agent.name}
                  agent={agent}
                  state={getAgentState(agent.name)}
                  isCurrent={STAGE_AGENT_MAP[workflow.current_stage] === agent.name}
                  onRegenerate={handleRegenerateStage}
                />
              ))}
            </div>

            {/* 完成后显示编辑入口 */}
            {workflow.current_stage === 'completed' && (
              <div className="bg-gradient-to-r from-green-50 to-emerald-50 rounded-2xl p-6 border-2 border-green-200">
                <div className="flex items-center gap-3 mb-4">
                  <span className="text-3xl">🎉</span>
                  <div>
                    <h3 className="text-lg font-bold text-gray-900">视频生成完成！</h3>
                    <p className="text-sm text-gray-600">点击下方按钮进入时间轴编辑器调整字幕和时长</p>
                  </div>
                </div>
                <button
                  onClick={() => setPhase('edit')}
                  className="w-full px-6 py-3 rounded-xl font-semibold text-white bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 hover:scale-[1.02] transition-transform"
                >
                  ✏️ 进入时间轴编辑器
                </button>
              </div>
            )}

            {/* 失败时显示错误 */}
            {workflow.current_stage === 'failed' && workflow.error_message && (
              <div className="bg-red-50 rounded-2xl p-5 border-2 border-red-200">
                <p className="text-red-700 font-medium">❌ 生成失败</p>
                <p className="text-red-600 text-sm mt-1">{workflow.error_message}</p>
              </div>
            )}
          </div>
        )}

        {/* ============ 编辑阶段 ============ */}
        {phase === 'edit' && workflow && (
          <div className="max-w-6xl mx-auto">
            <div className="mb-4 flex items-center gap-3">
              <button
                onClick={() => setPhase('run')}
                className="px-4 py-2 rounded-lg text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200"
              >
                ← 返回执行视图
              </button>
              <h2 className="text-lg font-bold text-gray-900">
                时间轴编辑 - {workflow.title}
              </h2>
            </div>
            <TimelineEditor
              workflowId={workflowId}
              panels={workflow.panels || []}
              videoUrl={workflow.video_url}
              onUpdate={() => loadWorkflowState()}
              onRecompose={handleRecompose}
            />
          </div>
        )}
      </div>
    </div>
  );
}

export default WorkflowPage;
