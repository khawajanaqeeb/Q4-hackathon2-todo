import React from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { RootState } from '@/store';
import { setInputText, setCommandSuggestionsVisible } from '@/store/slices/uiSlice';

const CommandSuggestions: React.FC = () => {
  const dispatch = useDispatch();
  const { commandSuggestionsVisible } = useSelector((state: RootState) => state.ui);
  const { theme } = useSelector((state: RootState) => state.ui);

  // Sample command suggestions - in a real app these would come from the store
  const suggestions = [
    { id: '1', text: 'Create a new task: Buy groceries', category: 'task' },
    { id: '2', text: 'List my tasks', category: 'task' },
    { id: '3', text: 'Mark task as complete', category: 'task' },
    { id: '4', text: 'Show urgent tasks', category: 'task' },
  ];

  const handleSuggestionClick = (suggestionText: string) => {
    // Populate the input field with the suggestion
    dispatch(setInputText(suggestionText.replace(/^(Create a new task:|List my|Mark task as|Show)/, '').trim()));
    // Hide suggestions
    dispatch(setCommandSuggestionsVisible(false));
  };

  if (!commandSuggestionsVisible || suggestions.length === 0) {
    return null;
  }

  return (
    <div
      className={`absolute bottom-full left-0 right-0 mb-2 rounded-lg shadow-lg z-10 max-h-60 overflow-y-auto ${
        theme === 'dark' ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'
      } border`}
      role="listbox"
      aria-label="Command suggestions"
    >
      <ul className="divide-y divide-gray-200 dark:divide-gray-700">
        {suggestions.map((suggestion) => (
          <li
            key={suggestion.id}
            className={`p-3 cursor-pointer hover:${
              theme === 'dark' ? 'bg-gray-700' : 'bg-gray-100'
            }`}
            onClick={() => handleSuggestionClick(suggestion.text)}
            role="option"
            tabIndex={0}
            aria-label={`Suggestion: ${suggestion.text}`}
          >
            <div className="flex justify-between items-center">
              <span className="font-medium">{suggestion.text}</span>
              <span className="text-xs px-2 py-1 rounded-full bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-100">
                {suggestion.category}
              </span>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default CommandSuggestions;