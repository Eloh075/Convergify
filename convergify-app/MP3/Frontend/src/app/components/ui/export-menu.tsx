import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/app/components/ui/dropdown-menu';
import { Button } from '@/app/components/ui/button';
import { Download, FileText, FolderArchive, BarChart3, ChevronDown } from 'lucide-react';

interface ExportMenuProps {
  onExportCurrent: () => void;
  onExportWithAnalysis?: () => void;
  onExportAll?: () => void;
  variant?: 'default' | 'outline';
}

export function ExportMenu({
  onExportCurrent,
  onExportWithAnalysis,
  onExportAll,
  variant = 'outline',
}: ExportMenuProps) {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant={variant} className="gap-2">
          <Download className="w-4 h-4" />
          Export
          <ChevronDown className="w-3 h-3 ml-1" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-56">
        <DropdownMenuItem onClick={onExportCurrent} className="gap-2">
          <FileText className="w-4 h-4" />
          Export Current Resume
        </DropdownMenuItem>
        {onExportWithAnalysis && (
          <DropdownMenuItem onClick={onExportWithAnalysis} className="gap-2">
            <BarChart3 className="w-4 h-4" />
            Export with Analysis Report
          </DropdownMenuItem>
        )}
        {onExportAll && (
          <DropdownMenuItem onClick={onExportAll} className="gap-2">
            <FolderArchive className="w-4 h-4" />
            Export All Versions (ZIP)
          </DropdownMenuItem>
        )}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
