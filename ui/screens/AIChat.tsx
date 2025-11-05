/**
 * QWAMOS AI Chat Interface
 *
 * Interactive chat UI for communicating with AI assistants
 */

import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TextInput,
  TouchableOpacity,
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { AIManager } from '../services/AIManager';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  serviceId: string;
}

interface AIChatProps {
  serviceId: 'kali-gpt' | 'claude' | 'chatgpt';
  serviceName: string;
  onBack?: () => void;
}

export const AIChatScreen: React.FC<AIChatProps> = ({
  serviceId,
  serviceName,
  onBack,
}) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [context, setContext] = useState<any>({});
  const scrollViewRef = useRef<ScrollView>(null);

  useEffect(() => {
    // Load conversation history from storage
    loadConversationHistory();
  }, [serviceId]);

  /**
   * Load previous conversation history
   */
  const loadConversationHistory = async () => {
    try {
      const history = await AIManager.getConversationHistory(serviceId);
      if (history) {
        setMessages(history);
        setContext(history[history.length - 1]?.context || {});
      }
    } catch (error) {
      console.error('Failed to load conversation history:', error);
    }
  };

  /**
   * Save conversation history
   */
  const saveConversationHistory = async (updatedMessages: Message[]) => {
    try {
      await AIManager.saveConversationHistory(serviceId, updatedMessages);
    } catch (error) {
      console.error('Failed to save conversation history:', error);
    }
  };

  /**
   * Send message to AI
   */
  const sendMessage = async () => {
    if (!inputText.trim() || loading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: inputText.trim(),
      timestamp: new Date(),
      serviceId,
    };

    // Add user message to chat
    const updatedMessages = [...messages, userMessage];
    setMessages(updatedMessages);
    setInputText('');

    // Scroll to bottom
    setTimeout(() => {
      scrollViewRef.current?.scrollToEnd({ animated: true });
    }, 100);

    try {
      setLoading(true);

      // Query AI service
      const response = await AIManager.query(
        serviceId,
        userMessage.content,
        context
      );

      // Add AI response to chat
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.content || response,
        timestamp: new Date(),
        serviceId,
      };

      const finalMessages = [...updatedMessages, assistantMessage];
      setMessages(finalMessages);

      // Update context if provided
      if (response.context) {
        setContext(response.context);
      }

      // Save conversation
      await saveConversationHistory(finalMessages);

      // Scroll to bottom
      setTimeout(() => {
        scrollViewRef.current?.scrollToEnd({ animated: true });
      }, 100);
    } catch (error: any) {
      console.error('Failed to send message:', error);

      // Add error message
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `Error: ${error.message || 'Failed to get response'}`,
        timestamp: new Date(),
        serviceId,
      };

      setMessages([...updatedMessages, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Clear conversation
   */
  const clearConversation = () => {
    setMessages([]);
    setContext({});
    saveConversationHistory([]);
  };

  /**
   * Render message bubble
   */
  const renderMessage = (message: Message) => {
    const isUser = message.role === 'user';

    return (
      <View
        key={message.id}
        style={[
          styles.messageBubble,
          isUser ? styles.userBubble : styles.assistantBubble,
        ]}
      >
        <Text style={styles.messageRole}>
          {isUser ? 'You' : serviceName}
        </Text>
        <Text
          style={[
            styles.messageText,
            isUser ? styles.userText : styles.assistantText,
          ]}
        >
          {message.content}
        </Text>
        <Text style={styles.messageTime}>
          {message.timestamp.toLocaleTimeString()}
        </Text>
      </View>
    );
  };

  /**
   * Get service-specific suggestions
   */
  const getSuggestions = (): string[] => {
    switch (serviceId) {
      case 'kali-gpt':
        return [
          'How do I scan for open ports?',
          'Explain SQL injection',
          'What is a buffer overflow?',
        ];
      case 'claude':
        return [
          'Explain post-quantum cryptography',
          'How does Tor work?',
          'Analyze this code for vulnerabilities',
        ];
      case 'chatgpt':
        return [
          'Write a Python script',
          'Explain this concept',
          'Help me debug this error',
        ];
      default:
        return [];
    }
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      keyboardVerticalOffset={Platform.OS === 'ios' ? 64 : 0}
    >
      {/* Header */}
      <View style={styles.header}>
        {onBack && (
          <TouchableOpacity onPress={onBack} style={styles.backButton}>
            <Text style={styles.backButtonText}>← Back</Text>
          </TouchableOpacity>
        )}
        <Text style={styles.title}>{serviceName}</Text>
        <TouchableOpacity onPress={clearConversation} style={styles.clearButton}>
          <Text style={styles.clearButtonText}>Clear</Text>
        </TouchableOpacity>
      </View>

      {/* Messages */}
      <ScrollView
        ref={scrollViewRef}
        style={styles.messagesContainer}
        contentContainerStyle={styles.messagesContent}
      >
        {messages.length === 0 && (
          <View style={styles.emptyState}>
            <Text style={styles.emptyTitle}>Start a conversation</Text>
            <Text style={styles.emptySubtitle}>
              Ask {serviceName} anything
            </Text>

            {/* Suggestions */}
            <View style={styles.suggestionsContainer}>
              <Text style={styles.suggestionsTitle}>Suggestions:</Text>
              {getSuggestions().map((suggestion, index) => (
                <TouchableOpacity
                  key={index}
                  style={styles.suggestionChip}
                  onPress={() => setInputText(suggestion)}
                >
                  <Text style={styles.suggestionText}>{suggestion}</Text>
                </TouchableOpacity>
              ))}
            </View>
          </View>
        )}

        {messages.map(renderMessage)}

        {/* Loading indicator */}
        {loading && (
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="small" color="#007AFF" />
            <Text style={styles.loadingText}>
              {serviceName} is thinking...
            </Text>
          </View>
        )}
      </ScrollView>

      {/* Input area */}
      <View style={styles.inputContainer}>
        <TextInput
          style={styles.input}
          placeholder={`Message ${serviceName}...`}
          value={inputText}
          onChangeText={setInputText}
          onSubmitEditing={sendMessage}
          multiline
          maxLength={4000}
          editable={!loading}
        />
        <TouchableOpacity
          style={[
            styles.sendButton,
            (!inputText.trim() || loading) && styles.sendButtonDisabled,
          ]}
          onPress={sendMessage}
          disabled={!inputText.trim() || loading}
        >
          <Text style={styles.sendButtonText}>➤</Text>
        </TouchableOpacity>
      </View>

      {/* Privacy notice for cloud services */}
      {(serviceId === 'claude' || serviceId === 'chatgpt') && (
        <View style={styles.privacyNotice}>
          <Text style={styles.privacyText}>
            🔒 Routed via Tor • PII sanitized • End-to-end encrypted
          </Text>
        </View>
      )}
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F5F5F5',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: 16,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E0E0E0',
  },
  title: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
  },
  backButton: {
    padding: 8,
  },
  backButtonText: {
    fontSize: 16,
    color: '#007AFF',
  },
  clearButton: {
    padding: 8,
  },
  clearButtonText: {
    fontSize: 14,
    color: '#FF3B30',
  },
  messagesContainer: {
    flex: 1,
  },
  messagesContent: {
    padding: 16,
  },
  emptyState: {
    alignItems: 'center',
    paddingTop: 60,
  },
  emptyTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 8,
  },
  emptySubtitle: {
    fontSize: 16,
    color: '#666',
    marginBottom: 32,
  },
  suggestionsContainer: {
    width: '100%',
  },
  suggestionsTitle: {
    fontSize: 14,
    color: '#666',
    marginBottom: 12,
    fontWeight: '600',
  },
  suggestionChip: {
    backgroundColor: '#E3F2FD',
    borderRadius: 20,
    paddingHorizontal: 16,
    paddingVertical: 10,
    marginBottom: 8,
  },
  suggestionText: {
    fontSize: 14,
    color: '#007AFF',
  },
  messageBubble: {
    maxWidth: '80%',
    marginBottom: 16,
    padding: 12,
    borderRadius: 12,
  },
  userBubble: {
    alignSelf: 'flex-end',
    backgroundColor: '#007AFF',
  },
  assistantBubble: {
    alignSelf: 'flex-start',
    backgroundColor: '#FFFFFF',
    borderWidth: 1,
    borderColor: '#E0E0E0',
  },
  messageRole: {
    fontSize: 11,
    fontWeight: 'bold',
    marginBottom: 4,
    opacity: 0.7,
  },
  messageText: {
    fontSize: 15,
    lineHeight: 20,
  },
  userText: {
    color: '#FFFFFF',
  },
  assistantText: {
    color: '#333',
  },
  messageTime: {
    fontSize: 10,
    marginTop: 4,
    opacity: 0.5,
  },
  loadingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    alignSelf: 'flex-start',
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 12,
    marginBottom: 16,
  },
  loadingText: {
    marginLeft: 8,
    fontSize: 14,
    color: '#666',
  },
  inputContainer: {
    flexDirection: 'row',
    padding: 12,
    backgroundColor: '#FFFFFF',
    borderTopWidth: 1,
    borderTopColor: '#E0E0E0',
    alignItems: 'flex-end',
  },
  input: {
    flex: 1,
    backgroundColor: '#F5F5F5',
    borderRadius: 20,
    paddingHorizontal: 16,
    paddingVertical: 10,
    fontSize: 15,
    maxHeight: 100,
    marginRight: 8,
  },
  sendButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#007AFF',
    justifyContent: 'center',
    alignItems: 'center',
  },
  sendButtonDisabled: {
    backgroundColor: '#CCC',
  },
  sendButtonText: {
    fontSize: 20,
    color: '#FFFFFF',
  },
  privacyNotice: {
    backgroundColor: '#FFF9C4',
    padding: 8,
    alignItems: 'center',
  },
  privacyText: {
    fontSize: 11,
    color: '#555',
  },
});
