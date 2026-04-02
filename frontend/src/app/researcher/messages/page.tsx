'use client';

import { useState } from 'react';
import { useApiQuery } from '@/hooks/useApiQuery';
import { useApiMutation } from '@/hooks/useApiMutation';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PortalShell from '@/components/portal/PortalShell';
import { getPortalNavItems } from '@/lib/portal';
import { useAuthStore } from '@/store/authStore';
import Spinner from '@/components/ui/Spinner';
import Button from '@/components/ui/Button';
import Textarea from '@/components/ui/Textarea';
import Avatar from '@/components/ui/Avatar';
import EmptyState from '@/components/ui/EmptyState';
import Modal from '@/components/ui/Modal';
import Input from '@/components/ui/Input';

interface Conversation {
  conversation_id: string;
  other_user: {
    id: string;
    email: string;
    role: string;
  } | null;
  last_message: {
    text: string;
    created_at: string;
    sender_id: string;
  } | null;
  unread_count: number;
  last_message_at: string | null;
  created_at: string;
}

interface Message {
  id: string;
  conversation_id: string;
  sender_id: string;
  recipient_id: string;
  message_text: string;
  is_read: boolean;
  read_at: string | null;
  created_at: string;
  updated_at: string;
  edited: boolean;
}

export default function ResearcherMessagesPage() {
  const user = useAuthStore((state) => state.user);
  const [selectedConversation, setSelectedConversation] = useState<string | null>(null);
  const [newMessage, setNewMessage] = useState('');
  const [showNewMessageModal, setShowNewMessageModal] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedUser, setSelectedUser] = useState<{id: string; email: string; full_name: string | null; role: string} | null>(null);
  const [newMessageText, setNewMessageText] = useState('');

  // Search users
  const { data: searchResults, isLoading: searchLoading } = useApiQuery<{
    users: Array<{id: string; email: string; full_name: string | null; role: string}>;
    total: number;
  }>(`/users/search?q=${encodeURIComponent(searchQuery)}`, { 
    enabled: searchQuery.length >= 2 
  });

  // Fetch conversations
  const { data: conversationsData, isLoading: conversationsLoading, refetch: refetchConversations } = useApiQuery<{
    conversations: Conversation[];
    total: number;
  }>('/messages/conversations', { enabled: !!user });

  // Fetch messages for selected conversation
  const { data: messagesData, isLoading: messagesLoading, refetch: refetchMessages } = useApiQuery<{
    messages: Message[];
    total: number;
    conversation_id: string;
  }>(`/messages/conversation/${selectedConversation}`, { 
    enabled: !!selectedConversation 
  });

  // Send message mutation
  const sendMessageMutation = useApiMutation<any, {
    recipient_id: string;
    message_text: string;
  }>('/messages', 'POST', {
    onSuccess: () => {
      setNewMessage('');
      refetchMessages();
      refetchConversations();
    }
  });

  // Mark conversation as read mutation
  const markAsReadMutation = useApiMutation<any, {}>(`/messages/conversation/${selectedConversation}/read-all`, 'POST', {
    onSuccess: () => {
      refetchConversations();
    }
  });

  const conversations = conversationsData?.conversations || [];
  const messages = messagesData?.messages || [];
  const selectedConv = conversations.find(c => c.conversation_id === selectedConversation);

  const handleConversationSelect = (conversationId: string) => {
    setSelectedConversation(conversationId);
    // Mark as read when opening conversation
    const conv = conversations.find(c => c.conversation_id === conversationId);
    if (conv && conv.unread_count > 0) {
      markAsReadMutation.mutate({});
    }
  };

  const handleSendMessage = () => {
    if (!newMessage.trim() || !selectedConv?.other_user) return;
    
    sendMessageMutation.mutate({
      recipient_id: selectedConv.other_user.id,
      message_text: newMessage.trim()
    });
  };

  // Send message mutation for new conversations
  const sendNewMessageMutation = useApiMutation<any, {
    recipient_id: string;
    message_text: string;
  }>('/messages', 'POST', {
    onSuccess: () => {
      setShowNewMessageModal(false);
      setSearchQuery('');
      setSelectedUser(null);
      setNewMessageText('');
      refetchConversations();
    }
  });

  const handleStartNewConversation = () => {
    if (!newMessageText.trim() || !selectedUser) return;
    
    sendNewMessageMutation.mutate({
      recipient_id: selectedUser.id,
      message_text: newMessageText.trim()
    });
  };

  const formatTime = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = (now.getTime() - date.getTime()) / (1000 * 60 * 60);
    
    if (diffInHours < 24) {
      return date.toLocaleTimeString('en-US', { 
        hour: 'numeric', 
        minute: '2-digit',
        hour12: true 
      });
    } else if (diffInHours < 168) { // 7 days
      return date.toLocaleDateString('en-US', { weekday: 'short' });
    } else {
      return date.toLocaleDateString('en-US', { 
        month: 'short', 
        day: 'numeric' 
      });
    }
  };

  const getRoleColor = (role: string) => {
    switch (role) {
      case 'researcher': return 'bg-[#3b82f6] text-white';
      case 'organization': return 'bg-[#10b981] text-white';
      case 'triage_specialist': return 'bg-[#f59e0b] text-white';
      case 'finance_officer': return 'bg-[#8b5cf6] text-white';
      case 'admin': return 'bg-[#ef4444] text-white';
      default: return 'bg-[#6b7280] text-white';
    }
  };

  const getRoleLabel = (role: string) => {
    switch (role) {
      case 'researcher': return 'Researcher';
      case 'organization': return 'Organization';
      case 'triage_specialist': return 'Triage';
      case 'finance_officer': return 'Finance';
      case 'admin': return 'Admin';
      default: return role;
    }
  };

  return (
    <ProtectedRoute allowedRoles={['researcher']}>
      {user ? (
        <PortalShell
          user={user}
          title="Messages"
          subtitle="Communicate with organizations, staff, and other researchers about reports and engagements."
          navItems={getPortalNavItems(user.role)}
        >
          <div className="flex h-[600px] rounded-2xl bg-[#faf6f1] border border-[#e6ddd4] overflow-hidden">
            {/* Conversations List */}
            <div className="w-1/3 border-r border-[#e6ddd4] flex flex-col">
              <div className="p-4 border-b border-[#e6ddd4] flex items-center justify-between">
                <h3 className="font-semibold text-[#2d2a26]">Conversations</h3>
                <Button
                  onClick={() => setShowNewMessageModal(true)}
                  className="text-xs px-3 py-1"
                >
                  + New
                </Button>
              </div>
              
              <div className="flex-1 overflow-y-auto">
                {conversationsLoading ? (
                  <div className="flex justify-center items-center py-8">
                    <Spinner size="sm" />
                  </div>
                ) : conversations.length === 0 ? (
                  <div className="p-4 text-center">
                    <p className="text-sm text-[#6d6760]">No conversations yet</p>
                    <p className="text-xs text-[#8b8177] mt-1">
                      Messages will appear here when you communicate with organizations or staff
                    </p>
                  </div>
                ) : (
                  <div className="space-y-1 p-2">
                    {conversations.map((conversation) => (
                      <button
                        key={conversation.conversation_id}
                        onClick={() => handleConversationSelect(conversation.conversation_id)}
                        className={`w-full text-left p-3 rounded-xl transition-colors ${
                          selectedConversation === conversation.conversation_id
                            ? 'bg-white border border-[#d8d0c8]'
                            : 'hover:bg-[#f3f0eb]'
                        }`}
                      >
                        <div className="flex items-start gap-3">
                          <Avatar 
                            fallback={conversation.other_user?.email || 'Unknown'} 
                            size="sm" 
                          />
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center justify-between mb-1">
                              <p className="text-sm font-medium text-[#2d2a26] truncate">
                                {conversation.other_user?.email || 'Unknown User'}
                              </p>
                              {conversation.unread_count > 0 && (
                                <span className="bg-[#ef2330] text-white text-xs rounded-full px-2 py-0.5 min-w-[20px] text-center">
                                  {conversation.unread_count}
                                </span>
                              )}
                            </div>
                            
                            {conversation.other_user && (
                              <span className={`inline-block text-xs px-2 py-0.5 rounded-full mb-1 ${getRoleColor(conversation.other_user.role)}`}>
                                {getRoleLabel(conversation.other_user.role)}
                              </span>
                            )}
                            
                            {conversation.last_message && (
                              <div className="flex items-center justify-between">
                                <p className="text-xs text-[#6d6760] truncate">
                                  {conversation.last_message.text}
                                </p>
                                <span className="text-xs text-[#8b8177] ml-2">
                                  {formatTime(conversation.last_message.created_at)}
                                </span>
                              </div>
                            )}
                          </div>
                        </div>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Message Thread */}
            <div className="flex-1 flex flex-col">
              {selectedConversation ? (
                <>
                  {/* Thread Header */}
                  <div className="p-4 border-b border-[#e6ddd4] bg-white">
                    <div className="flex items-center gap-3">
                      <Avatar 
                        fallback={selectedConv?.other_user?.email || 'Unknown'} 
                        size="sm" 
                      />
                      <div>
                        <p className="font-medium text-[#2d2a26]">
                          {selectedConv?.other_user?.email || 'Unknown User'}
                        </p>
                        {selectedConv?.other_user && (
                          <span className={`inline-block text-xs px-2 py-0.5 rounded-full ${getRoleColor(selectedConv.other_user.role)}`}>
                            {getRoleLabel(selectedConv.other_user.role)}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Messages */}
                  <div className="flex-1 overflow-y-auto p-4 space-y-4">
                    {messagesLoading ? (
                      <div className="flex justify-center items-center py-8">
                        <Spinner size="sm" />
                      </div>
                    ) : messages.length === 0 ? (
                      <div className="text-center py-8">
                        <p className="text-sm text-[#6d6760]">No messages yet</p>
                        <p className="text-xs text-[#8b8177] mt-1">Start the conversation below</p>
                      </div>
                    ) : (
                      messages.map((message) => {
                        const isFromMe = message.sender_id === user.id;
                        return (
                          <div
                            key={message.id}
                            className={`flex ${isFromMe ? 'justify-end' : 'justify-start'}`}
                          >
                            <div className={`max-w-[70%] ${isFromMe ? 'order-2' : 'order-1'}`}>
                              <div
                                className={`rounded-2xl px-4 py-2 ${
                                  isFromMe
                                    ? 'bg-[#ef2330] text-white'
                                    : 'bg-white border border-[#e6ddd4] text-[#2d2a26]'
                                }`}
                              >
                                <p className="text-sm whitespace-pre-wrap">{message.message_text}</p>
                                {message.edited && (
                                  <p className="text-xs opacity-70 mt-1">(edited)</p>
                                )}
                              </div>
                              <div className={`flex items-center gap-2 mt-1 text-xs text-[#8b8177] ${isFromMe ? 'justify-end' : 'justify-start'}`}>
                                <span>{formatTime(message.created_at)}</span>
                                {isFromMe && message.is_read && (
                                  <span>• Read</span>
                                )}
                              </div>
                            </div>
                          </div>
                        );
                      })
                    )}
                  </div>

                  {/* Message Input */}
                  <div className="p-4 border-t border-[#e6ddd4] bg-white">
                    <div className="flex gap-3">
                      <Textarea
                        value={newMessage}
                        onChange={(e) => setNewMessage(e.target.value)}
                        placeholder="Type your message..."
                        rows={2}
                        className="flex-1 resize-none"
                        onKeyDown={(e) => {
                          if (e.key === 'Enter' && !e.shiftKey) {
                            e.preventDefault();
                            handleSendMessage();
                          }
                        }}
                      />
                      <Button
                        onClick={handleSendMessage}
                        disabled={!newMessage.trim() || sendMessageMutation.isLoading}
                        className="self-end"
                      >
                        {sendMessageMutation.isLoading ? <Spinner size="sm" /> : 'Send'}
                      </Button>
                    </div>
                    <p className="text-xs text-[#8b8177] mt-2">
                      Press Enter to send, Shift+Enter for new line
                    </p>
                  </div>
                </>
              ) : (
                <div className="flex-1 flex items-center justify-center">
                  <EmptyState
                    title="Select a conversation"
                    description="Choose a conversation from the list to start messaging"
                    icon="💬"
                  />
                </div>
              )}
            </div>
          </div>

          {/* New Message Modal */}
          {showNewMessageModal && (
            <Modal
              isOpen={showNewMessageModal}
              onClose={() => {
                setShowNewMessageModal(false);
                setSearchQuery('');
                setSelectedUser(null);
                setNewMessageText('');
              }}
              title="Start New Conversation"
            >
              <div className="space-y-4">
                {!selectedUser ? (
                  <>
                    <div>
                      <label className="block text-sm font-medium text-[#2d2a26] mb-1">
                        Search for a user
                      </label>
                      <Input
                        type="text"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        placeholder="Type email or name..."
                      />
                      <p className="text-xs text-[#8b8177] mt-1">
                        Search for organizations, staff, or other researchers
                      </p>
                    </div>

                    {/* Search Results */}
                    {searchQuery.length >= 2 && (
                      <div className="border border-[#e6ddd4] rounded-xl max-h-60 overflow-y-auto">
                        {searchLoading ? (
                          <div className="flex justify-center items-center py-8">
                            <Spinner size="sm" />
                          </div>
                        ) : searchResults && searchResults.users.length > 0 ? (
                          <div className="divide-y divide-[#e6ddd4]">
                            {searchResults.users.map((user) => (
                              <button
                                key={user.id}
                                onClick={() => setSelectedUser(user)}
                                className="w-full text-left p-3 hover:bg-[#f3f0eb] transition-colors flex items-center gap-3"
                              >
                                <Avatar fallback={user.email} size="sm" />
                                <div className="flex-1 min-w-0">
                                  <p className="text-sm font-medium text-[#2d2a26] truncate">
                                    {user.full_name || user.email}
                                  </p>
                                  <p className="text-xs text-[#6d6760] truncate">{user.email}</p>
                                  <span className={`inline-block text-xs px-2 py-0.5 rounded-full mt-1 ${getRoleColor(user.role)}`}>
                                    {getRoleLabel(user.role)}
                                  </span>
                                </div>
                              </button>
                            ))}
                          </div>
                        ) : (
                          <div className="p-4 text-center text-sm text-[#6d6760]">
                            No users found
                          </div>
                        )}
                      </div>
                    )}
                  </>
                ) : (
                  <>
                    <div className="flex items-center gap-3 p-3 bg-[#f3f0eb] rounded-xl">
                      <Avatar fallback={selectedUser.email} size="sm" />
                      <div className="flex-1">
                        <p className="text-sm font-medium text-[#2d2a26]">
                          {selectedUser.full_name || selectedUser.email}
                        </p>
                        <p className="text-xs text-[#6d6760]">{selectedUser.email}</p>
                      </div>
                      <button
                        onClick={() => setSelectedUser(null)}
                        className="text-xs text-[#ef2330] hover:underline"
                      >
                        Change
                      </button>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-[#2d2a26] mb-1">
                        Message
                      </label>
                      <Textarea
                        value={newMessageText}
                        onChange={(e) => setNewMessageText(e.target.value)}
                        placeholder="Type your message..."
                        rows={4}
                        autoFocus
                      />
                    </div>

                    <div className="flex gap-3 justify-end">
                      <Button
                        onClick={() => setSelectedUser(null)}
                        className="bg-[#6d6760] hover:bg-[#5d5750]"
                      >
                        Back
                      </Button>
                      <Button
                        onClick={handleStartNewConversation}
                        disabled={!newMessageText.trim() || sendMessageMutation.isLoading}
                      >
                        {sendMessageMutation.isLoading ? <Spinner size="sm" /> : 'Send Message'}
                      </Button>
                    </div>
                  </>
                )}
              </div>
            </Modal>
          )}
        </PortalShell>
      ) : null}
    </ProtectedRoute>
  );
}