import React, { useState, useEffect } from 'react';

/**
 * 字幕配置面板
 * 支持位置、字号、颜色、描边、背景、动画
 * 提供 CSS 模拟预览
 */
function SubtitleConfigPanel({ value, onChange, presetText = '这是字幕预览文字' }) {
  // 位置选项
  const POSITION_OPTIONS = [
    { value: 'top_left', label: '顶部左对齐' },
    { value: 'top_center', label: '顶部居中' },
    { value: 'top_right', label: '顶部右对齐' },
    { value: 'middle_left', label: '中部左对齐' },
    { value: 'middle_center', label: '中部居中' },
    { value: 'middle_right', label: '中部右对齐' },
    { value: 'bottom_left', label: '底部左对齐' },
    { value: 'bottom_center', label: '底部居中' },
    { value: 'bottom_right', label: '底部右对齐' },
  ];

  // 动画选项
  const ANIMATION_OPTIONS = [
    { value: 'none', label: '无动画' },
    { value: 'fade_in', label: '淡入' },
  ];

  // 字体大小转 CSS 像素
  const fontSizeToPx = (size) => Math.max(12, size / 2);

  // 计算位置对应的 CSS
  const getPositionStyle = (position) => {
    const vAlign = position.startsWith('top') ? 'flex-start' :
                   position.startsWith('middle') ? 'center' : 'flex-end';
    const hAlign = position.endsWith('left') ? 'flex-start' :
                   position.endsWith('right') ? 'flex-end' : 'center';
    return { alignItems: hAlign, justifyContent: vAlign };
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <label className="block text-sm font-semibold text-gray-700">
          字幕配置
        </label>
        <label className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={value.enabled}
            onChange={(e) => onChange({ ...value, enabled: e.target.checked })}
            className="w-4 h-4 text-blue-600 rounded"
          />
          <span className="text-sm text-gray-600">启用字幕</span>
        </label>
      </div>

      {value.enabled && (
        <>
          {/* 位置选择 */}
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">
              字幕位置
            </label>
            <select
              value={value.position}
              onChange={(e) => onChange({ ...value, position: e.target.value })}
              className="w-full px-3 py-2 rounded-lg border-2 border-gray-200 focus:border-blue-500 outline-none text-sm"
            >
              {POSITION_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </select>
          </div>

          {/* 字号 */}
          <div>
            <div className="flex justify-between mb-1">
              <label className="text-xs font-medium text-gray-600">字号</label>
              <span className="text-xs text-gray-500">{value.font_size}</span>
            </div>
            <input
              type="range"
              min="16"
              max="96"
              value={value.font_size}
              onChange={(e) => onChange({ ...value, font_size: parseInt(e.target.value) })}
              className="w-full"
            />
          </div>

          {/* 颜色 */}
          <div className="grid grid-cols-3 gap-2">
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">文字色</label>
              <input
                type="color"
                value={value.font_color}
                onChange={(e) => onChange({ ...value, font_color: e.target.value })}
                className="w-full h-8 rounded cursor-pointer"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">描边色</label>
              <input
                type="color"
                value={value.outline_color}
                onChange={(e) => onChange({ ...value, outline_color: e.target.value })}
                className="w-full h-8 rounded cursor-pointer"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 mb-1">背景色</label>
              <input
                type="color"
                value={value.bg_color.slice(0, 7)}
                onChange={(e) => onChange({ ...value, bg_color: e.target.value + '80' })}
                className="w-full h-8 rounded cursor-pointer"
              />
            </div>
          </div>

          {/* 描边粗细 */}
          <div>
            <div className="flex justify-between mb-1">
              <label className="text-xs font-medium text-gray-600">描边粗细</label>
              <span className="text-xs text-gray-500">{value.outline_width}</span>
            </div>
            <input
              type="range"
              min="0"
              max="6"
              value={value.outline_width}
              onChange={(e) => onChange({ ...value, outline_width: parseInt(e.target.value) })}
              className="w-full"
            />
          </div>

          {/* 背景框 + 动画 */}
          <div className="flex items-center gap-4">
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={value.bg_enabled}
                onChange={(e) => onChange({ ...value, bg_enabled: e.target.checked })}
                className="w-4 h-4 text-blue-600 rounded"
              />
              <span className="text-xs text-gray-600">背景框</span>
            </label>
            <select
              value={value.animation}
              onChange={(e) => onChange({ ...value, animation: e.target.value })}
              className="flex-1 px-3 py-1.5 rounded border-2 border-gray-200 text-xs outline-none"
            >
              {ANIMATION_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </select>
          </div>

          {/* 预览 */}
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-2">预览</label>
            <div
              className="relative w-full h-32 rounded-lg overflow-hidden border-2 border-gray-200"
              style={{
                background: 'linear-gradient(135deg, #4F46E5 0%, #7C3AED 50%, #EC4899 100%)',
              }}
            >
              <div
                className="absolute inset-0 flex p-3"
                style={getPositionStyle(value.position)}
              >
                <span
                  style={{
                    color: value.font_color,
                    fontSize: `${fontSizeToPx(value.font_size)}px`,
                    fontWeight: value.bold ? 'bold' : 'normal',
                    backgroundColor: value.bg_enabled ? value.bg_color : 'transparent',
                    padding: value.bg_enabled ? '2px 8px' : '0',
                    borderRadius: value.bg_enabled ? '4px' : '0',
                    textShadow: value.outline_width > 0
                      ? `${-value.outline_width}px 0 ${value.outline_color}, ${value.outline_width}px 0 ${value.outline_color}, 0 ${-value.outline_width}px ${value.outline_color}, 0 ${value.outline_width}px ${value.outline_color}`
                      : 'none',
                  }}
                >
                  {presetText}
                </span>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

// 默认配置
export const DEFAULT_SUBTITLE_CONFIG = {
  enabled: true,
  position: 'bottom_center',
  font_size: 48,
  font_color: '#FFFFFF',
  outline_color: '#000000',
  outline_width: 2,
  bold: true,
  bg_enabled: true,
  bg_color: '#00000080',
  margin_top: 30,
  margin_horizontal: 30,
  animation: 'none',
};

export default SubtitleConfigPanel;
