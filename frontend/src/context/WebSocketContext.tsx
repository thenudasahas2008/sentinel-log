import React, { createContext, useContext, useEffect, useState, useRef } from 'react';

interface WebSocketContextType {
  isConnected: boolean;
  isPaused: boolean;
  togglePause: () => void;
  lastMessage: any;
}

const WebSocketContext = createContext<WebSocketContextType>({
  isConnected: false,
  isPaused: false,
  togglePause: () => {},
  lastMessage: null
});

export const WebSocketProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isConnected, setIsConnected] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [lastMessage, setLastMessage] = useState<any>(null);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    const wsUrl = `${protocol}//${host}/api/v1/ws/live`;

    let socket: WebSocket;
    let reconnectTimer: any;

    const connect = () => {
      try {
        socket = new WebSocket(wsUrl);
        wsRef.current = socket;

        socket.onopen = () => {
          setIsConnected(true);
        };

        socket.onmessage = (event) => {
          if (!isPaused) {
            try {
              const data = JSON.parse(event.data);
              setLastMessage(data);
            } catch (err) {
              // Ignore non-json
            }
          }
        };

        socket.onclose = () => {
          setIsConnected(false);
          reconnectTimer = setTimeout(connect, 4000);
        };

        socket.onerror = () => {
          socket.close();
        };
      } catch (e) {
        reconnectTimer = setTimeout(connect, 4000);
      }
    };

    connect();

    return () => {
      clearTimeout(reconnectTimer);
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [isPaused]);

  const togglePause = () => setIsPaused(prev => !prev);

  return (
    <WebSocketContext.Provider value={{ isConnected, isPaused, togglePause, lastMessage }}>
      {children}
    </WebSocketContext.Provider>
  );
};

export const useWebSocket = () => useContext(WebSocketContext);
