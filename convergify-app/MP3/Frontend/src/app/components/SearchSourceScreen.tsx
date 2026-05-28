import { useState } from 'react';
import { Upload, FileText, Sparkles } from 'lucide-react';
import { Button } from '@/app/components/ui/button';
import { Input } from '@/app/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/app/components/ui/select';

interface SearchSourceScreenProps {
  onStartDiscovery: (params: {
    jobTitle: string;
    jobLevel: string;
    resumeFile: File;
  }) => void;
}

export function SearchSourceScreen({ onStartDiscovery }: SearchSourceScreenProps) {
  const [jobTitle, setJobTitle] = useState('');
  const [jobLevel, setJobLevel] = useState('');
  const [resumeFile, setResumeFile] = useState<File | null>(null);

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setResumeFile(file);
    }
  };

  const canStart = jobTitle.trim() && jobLevel && resumeFile;

  const handleSubmit = () => {
    if (canStart) {
      onStartDiscovery({
        jobTitle: jobTitle.trim(),
        jobLevel,
        resumeFile,
      });
    }
  };

  return (
    <div className="flex-1 flex items-center justify-center p-4 sm:p-8 lg:p-12" style={{ backgroundColor: '#F9FAFB' }}>
      <div className="w-full max-w-[800px] space-y-6">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl mb-4" style={{ backgroundColor: 'var(--primary-blue)' }}>
            <Sparkles className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-3xl font-semibold mb-2">Define Your Market</h1>
          <p className="text-gray-600 dark:text-gray-300">
            Tell us what you're looking for and we'll analyze the entire landscape
          </p>
        </div>

        {/* Market Definition Card */}
        <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-8 space-y-6">
          <div>
            <label className="block text-sm font-semibold mb-2">
              Job Title or Domain
            </label>
            <Input
              placeholder="e.g., Business Development, Product Manager, Data Analyst"
              value={jobTitle}
              onChange={(e) => setJobTitle(e.target.value)}
              className="h-12"
            />
            <p className="text-xs text-gray-500 mt-1">
              We'll find similar roles across the market
            </p>
          </div>

          <div>
            <label className="block text-sm font-semibold mb-2">
              Job Level
            </label>
            <Select value={jobLevel} onValueChange={setJobLevel}>
              <SelectTrigger className="h-12">
                <SelectValue placeholder="Select experience level..." />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="intern">Intern</SelectItem>
                <SelectItem value="junior">Junior (0-2 years)</SelectItem>
                <SelectItem value="mid">Mid-Level (3-5 years)</SelectItem>
                <SelectItem value="senior">Senior (5+ years)</SelectItem>
                <SelectItem value="lead">Lead/Principal</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* Resume Upload Card */}
        <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6">
          <label className="block text-sm font-semibold mb-4">
            Your Resume
          </label>

          {!resumeFile ? (
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-gray-400 transition-colors">
              <Upload className="w-10 h-10 text-gray-400 mx-auto mb-3" />
              <p className="text-sm font-medium mb-2">Drop your resume here</p>
              <p className="text-xs text-gray-500 mb-4">PDF format, up to 10MB</p>
              <input
                type="file"
                accept=".pdf"
                onChange={handleFileInput}
                className="hidden"
                id="resume-upload"
              />
              <label htmlFor="resume-upload">
                <Button variant="outline" className="cursor-pointer" asChild>
                  <span>Browse Files</span>
                </Button>
              </label>
            </div>
          ) : (
            <div className="flex items-center gap-4 p-4 bg-gray-50 rounded-lg">
              <div
                className="w-12 h-12 rounded-lg flex items-center justify-center flex-shrink-0"
                style={{ backgroundColor: 'var(--primary-blue)' }}
              >
                <FileText className="w-6 h-6 text-white" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="font-medium text-sm truncate">{resumeFile.name}</p>
                <p className="text-xs text-gray-500">
                  {(resumeFile.size / 1024).toFixed(0)} KB
                </p>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setResumeFile(null)}
              >
                Remove
              </Button>
            </div>
          )}
        </div>

        {/* CTA */}
        <Button
          size="lg"
          disabled={!canStart}
          onClick={handleSubmit}
          className="w-full h-14 text-base"
          style={{
            backgroundColor: canStart ? 'var(--primary-blue)' : undefined,
          }}
        >
          Start Market Discovery
        </Button>
      </div>
    </div>
  );
}
