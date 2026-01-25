import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { ThemePreference } from '@/types';

interface UIState {
  theme: ThemePreference;
  isTypingIndicatorVisible: boolean;
  commandSuggestionsVisible: boolean;
  inputText: string;
  isInputDisabled: boolean;
  scrollPosition: number;
  notification: {
    isVisible: boolean;
    message: string;
    type: 'info' | 'success' | 'warning' | 'error';
    duration: number;
  };
}

const initialState: UIState = {
  theme: 'light',
  isTypingIndicatorVisible: false,
  commandSuggestionsVisible: false,
  inputText: '',
  isInputDisabled: false,
  scrollPosition: 0,
  notification: {
    isVisible: false,
    message: '',
    type: 'info',
    duration: 3000,
  },
};

const uiSlice = createSlice({
  name: 'ui',
  initialState,
  reducers: {
    // Theme actions
    setTheme(state, action: PayloadAction<ThemePreference>) {
      state.theme = action.payload;
    },

    toggleTheme(state) {
      state.theme = state.theme === 'light' ? 'dark' : 'light';
    },

    // Input actions
    setInputText(state, action: PayloadAction<string>) {
      state.inputText = action.payload;
    },

    setInputDisabled(state, action: PayloadAction<boolean>) {
      state.isInputDisabled = action.payload;
    },

    // Typing indicator actions
    setTypingIndicatorVisible(state, action: PayloadAction<boolean>) {
      state.isTypingIndicatorVisible = action.payload;
    },

    // Command suggestions actions
    setCommandSuggestionsVisible(state, action: PayloadAction<boolean>) {
      state.commandSuggestionsVisible = action.payload;
    },

    // Scroll position actions
    setScrollPosition(state, action: PayloadAction<number>) {
      state.scrollPosition = action.payload;
    },

    // Notification actions
    showNotification(state, action: PayloadAction<{ message: string; type?: 'info' | 'success' | 'warning' | 'error'; duration?: number }>) {
      const { message, type = 'info', duration = 3000 } = action.payload;
      state.notification = {
        isVisible: true,
        message,
        type,
        duration,
      };
    },

    hideNotification(state) {
      state.notification.isVisible = false;
    },

    // Reset input
    resetInput(state) {
      state.inputText = '';
    },
  },
});

export const {
  setTheme,
  toggleTheme,
  setInputText,
  setInputDisabled,
  setTypingIndicatorVisible,
  setCommandSuggestionsVisible,
  setScrollPosition,
  showNotification,
  hideNotification,
  resetInput,
} = uiSlice.actions;

export default uiSlice.reducer;