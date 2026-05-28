import * as TooltipPrimitive from '@radix-ui/react-tooltip';
import { Info } from 'lucide-react';

interface InfoTooltipProps {
  content: string;
}

export function InfoTooltip({ content }: InfoTooltipProps) {
  return (
    <TooltipPrimitive.Provider>
      <TooltipPrimitive.Root>
        <TooltipPrimitive.Trigger asChild>
          <button className="inline-flex items-center justify-center ml-1 text-gray-400 hover:text-gray-600 transition-colors">
            <Info className="w-4 h-4" />
          </button>
        </TooltipPrimitive.Trigger>
        <TooltipPrimitive.Portal>
          <TooltipPrimitive.Content
            className="bg-gray-900 text-white text-xs rounded-lg px-3 py-2 max-w-[250px] z-50 shadow-lg"
            sideOffset={5}
          >
            {content}
            <TooltipPrimitive.Arrow className="fill-gray-900" />
          </TooltipPrimitive.Content>
        </TooltipPrimitive.Portal>
      </TooltipPrimitive.Root>
    </TooltipPrimitive.Provider>
  );
}
