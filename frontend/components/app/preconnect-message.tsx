'use client';

import { AnimatePresence, motion } from 'motion/react';
import { type ReceivedChatMessage } from '@livekit/components-react';
import { ShimmerText } from '@/components/livekit/shimmer-text';
import { cn } from '@/lib/utils';

const MotionMessage = motion.create('p');

const VIEW_MOTION_PROPS = {
  variants: {
    visible: {
      opacity: 1,
      transition: {
        ease: 'easeIn',
        duration: 0.5,
        delay: 0.8,
      },
    },
    hidden: {
      opacity: 0,
      transition: {
        ease: 'easeIn',
        duration: 0.5,
        delay: 0,
      },
    },
  },
  initial: 'hidden',
  animate: 'visible',
  exit: 'hidden',
};

interface PreConnectMessageProps {
  messages?: ReceivedChatMessage[];
  className?: string;
}

export function PreConnectMessage({ className, messages = [] }: PreConnectMessageProps) {
  return (
    <AnimatePresence>
      {messages.length === 0 && (
        <div className="pointer-events-none fixed inset-0 z-50 flex flex-col items-center justify-center overflow-hidden">
          <h1 className="mb-8 animate-pulse bg-gradient-to-r from-yellow-400 via-orange-500 to-pink-500 bg-clip-text px-4 text-center text-9xl font-black text-transparent drop-shadow-[0_0_30px_rgba(251,146,60,0.8)]">
            Voice Improve Battle
          </h1>
          <MotionMessage
            {...VIEW_MOTION_PROPS}
            aria-hidden={messages.length > 0}
            className={cn('pointer-events-none text-center', className)}
          >
            <ShimmerText className="text-sm font-semibold">
              Host is listening, show your talent
            </ShimmerText>
          </MotionMessage>
        </div>
      )}
    </AnimatePresence>
  );
}

