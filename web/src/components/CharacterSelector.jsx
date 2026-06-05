import React, { useState, useEffect } from 'react';
import { characterApi } from '../services/api';

/**
 * 角色选择器
 * 网格展示角色卡片，支持多选/单选
 */
function CharacterSelector({ value = [], onChange, multi = true }) {
  const [characters, setCharacters] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [keyword, setKeyword] = useState('');

  useEffect(() => {
    loadCharacters();
  }, [keyword]);

  const loadCharacters = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await characterApi.list(keyword || undefined);
      setCharacters(response.data?.items || []);
    } catch (err) {
      setError(err.message || '加载角色失败');
    } finally {
      setLoading(false);
    }
  };

  const toggleCharacter = (id) => {
    if (multi) {
      const newValue = value.includes(id)
        ? value.filter(v => v !== id)
        : [...value, id];
      onChange(newValue);
    } else {
      onChange(value.includes(id) ? [] : [id]);
    }
  };

  return (
    <div className="space-y-3">
      {/* 搜索框 */}
      <div className="relative">
        <input
          type="text"
          placeholder="搜索角色..."
          value={keyword}
          onChange={(e) => setKeyword(e.target.value)}
          className="w-full px-4 py-2 pl-10 rounded-lg border-2 border-gray-200 focus:border-blue-500 outline-none text-sm"
        />
        <svg className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
      </div>

      {/* 错误提示 */}
      {error && (
        <div className="p-3 rounded-lg bg-red-50 border border-red-200 text-red-600 text-sm">
          {error}
        </div>
      )}

      {/* 角色网格 */}
      {loading ? (
        <div className="text-center py-8 text-gray-500 text-sm">加载中...</div>
      ) : characters.length === 0 ? (
        <div className="text-center py-8 text-gray-500 text-sm">暂无可用角色</div>
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3 max-h-64 overflow-y-auto">
          {characters.map((char) => {
            const isSelected = value.includes(char.id);
            return (
              <div
                key={char.id}
                onClick={() => toggleCharacter(char.id)}
                className={`relative p-3 rounded-xl border-2 cursor-pointer transition-all ${
                  isSelected
                    ? 'border-blue-500 bg-blue-50 shadow-md'
                    : 'border-gray-200 hover:border-gray-300 hover:shadow-sm'
                }`}
              >
                {/* 选中标记 */}
                {isSelected && (
                  <div className="absolute top-2 right-2 w-5 h-5 rounded-full bg-blue-500 flex items-center justify-center">
                    <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                )}

                {/* 头像 + 名称 */}
                <div className="flex items-center gap-2 mb-1">
                  <div
                    className="w-10 h-10 rounded-full flex items-center justify-center text-2xl"
                    style={{
                      background: char.color || '#E5E7EB',
                    }}
                  >
                    {char.avatar || '👤'}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="font-semibold text-sm text-gray-900 truncate">
                      {char.name}
                    </div>
                    {char.is_system && (
                      <span className="text-xs text-blue-600">系统预置</span>
                    )}
                  </div>
                </div>

                {/* 描述 */}
                <p className="text-xs text-gray-500 line-clamp-2">
                  {char.description}
                </p>
              </div>
            );
          })}
        </div>
      )}

      {/* 已选数量提示 */}
      {value.length > 0 && (
        <p className="text-xs text-blue-600">
          已选择 {value.length} 个角色
        </p>
      )}
    </div>
  );
}

export default CharacterSelector;
