// Utility functions for Indian time (IST) handling
export class IndianTimeUtils {
  // Get current time in IST
  static getCurrentIST(): Date {
    const now = new Date();
    // IST is UTC+5:30
    const istOffset = 5.5 * 60 * 60 * 1000; // 5.5 hours in milliseconds
    const utc = now.getTime() + (now.getTimezoneOffset() * 60 * 1000);
    return new Date(utc + istOffset);
  }

  // Format time in IST format
  static formatIST(date: Date = new Date()): string {
    const istTime = this.getCurrentIST();
    return istTime.toLocaleString('en-IN', {
      timeZone: 'Asia/Kolkata',
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: true
    });
  }

  // Format just time in IST
  static formatISTTime(date: Date = new Date()): string {
    const istTime = this.getCurrentIST();
    return istTime.toLocaleString('en-IN', {
      timeZone: 'Asia/Kolkata',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: true
    });
  }

  // Format just date in IST
  static formatISTDate(date: Date = new Date()): string {
    const istTime = this.getCurrentIST();
    return istTime.toLocaleString('en-IN', {
      timeZone: 'Asia/Kolkata',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  }

  // Get session start time in IST
  static getSessionStartTime(): string {
    return this.formatIST();
  }

  // Calculate session duration
  static calculateSessionDuration(startTime: Date): string {
    const now = this.getCurrentIST();
    const start = new Date(startTime);
    const durationMs = now.getTime() - start.getTime();
    
    const hours = Math.floor(durationMs / (1000 * 60 * 60));
    const minutes = Math.floor((durationMs % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((durationMs % (1000 * 60)) / 1000);

    if (hours > 0) {
      return `${hours}h ${minutes}m ${seconds}s`;
    } else if (minutes > 0) {
      return `${minutes}m ${seconds}s`;
    } else {
      return `${seconds}s`;
    }
  }

  // Format countdown timer
  static formatCountdown(seconds: number): string {
    const hours = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;

    if (hours > 0) {
      return `${hours}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    } else {
      return `${mins}:${secs.toString().padStart(2, '0')}`;
    }
  }

  // Get timezone info
  static getTimezoneInfo(): string {
    return "IST (UTC+5:30)";
  }
}

// React hook for live IST time
import { useState, useEffect } from 'react';

export function useISTTime() {
  const [currentTime, setCurrentTime] = useState<string>('');

  useEffect(() => {
    const updateTime = () => {
      setCurrentTime(IndianTimeUtils.formatISTTime());
    };

    updateTime(); // Initial update
    const interval = setInterval(updateTime, 1000); // Update every second

    return () => clearInterval(interval);
  }, []);

  return currentTime;
}