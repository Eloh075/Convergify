import { useState, useCallback } from 'react';
import { Upload, FileText, X, AlertCircle, CheckCircle } from 'lucide-react';
import { useDropzone } from 'react-dropzone';
import { Button } from '@/app/components/ui/button';
import { Progress } from '@/app/components/ui/progress';
import { useUploadResume } from '@/hooks/useApi';
import { toast } from 'sonner';

interface ResumeUploadProps {
  onUploadComplete?: (resumeId: string) => void;
  onCancel?: () => void;
}

interface UploadState {
  file: File | null;
  uploading: boolean;
  progress: number;
  error: string | null;
  success: boolean;
  extractedText?: string;
}

export function ResumeUpload({ onUploadComplete, onCancel }: ResumeUploadProps) {
  const [uploadState, setUploadState] = useState<UploadState>({
    file: null,
    uploading: false,
    progress: 0,
    error: null,
    success: false,
  });

  const uploadMutation = useUploadResume();

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (file) {
      // Validate file type
      if (!file.type.includes('pdf') && !file.type.includes('doc') && !file.name.toLowerCase().endsWith('.txt')) {
        setUploadState(prev => ({
          ...prev,
          error: 'Please upload a PDF, Word document, or text file'
        }));
        return;
      }

      // Validate file size (10MB limit)
      if (file.size > 10 * 1024 * 1024) {
        setUploadState(prev => ({
          ...prev,
          error: 'File size must be less than 10MB'
        }));
        return;
      }

      setUploadState(prev => ({
        ...prev,
        file,
        error: null,
        success: false
      }));
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt']
    },
    multiple: false,
    disabled: uploadState.uploading
  });

  const handleUpload = async () => {
    if (!uploadState.file) return;

    setUploadState(prev => ({
      ...prev,
      uploading: true,
      progress: 0,
      error: null
    }));

    try {
      // Simulate progress updates
      const progressInterval = setInterval(() => {
        setUploadState(prev => ({
          ...prev,
          progress: Math.min(prev.progress + 10, 90)
        }));
      }, 200);

      const result = await uploadMutation.mutateAsync({
        file: uploadState.file,
        user_id: 'default-user' // In a real app, this would come from auth
      });

      clearInterval(progressInterval);

      setUploadState(prev => ({
        ...prev,
        uploading: false,
        progress: 100,
        success: true,
        extractedText: result.extracted_text
      }));

      // Call completion callback after a brief delay
      setTimeout(() => {
        if (onUploadComplete) {
          onUploadComplete(result.id);
        }
      }, 1500);

    } catch (error: any) {
      setUploadState(prev => ({
        ...prev,
        uploading: false,
        progress: 0,
        error: error.message || 'Upload failed. Please try again.'
      }));
    }
  };

  const handleRemoveFile = () => {
    setUploadState({
      file: null,
      uploading: false,
      progress: 0,
      error: null,
      success: false
    });
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="max-w-2xl mx-auto p-6">
      <div className="text-center mb-8">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-blue-100 mb-4">
          <Upload className="w-8 h-8 text-blue-600" />
        </div>
        <h2 className="text-2xl font-semibold mb-2 dark:text-white">Upload Your Resume</h2>
        <p className="text-gray-600 dark:text-gray-300">
          Upload your resume to get started with AI-powered career analysis
        </p>
      </div>

      {!uploadState.file ? (
        // File Drop Zone
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-xl p-6 sm:p-8 lg:p-12 text-center transition-colors cursor-pointer ${
            isDragActive
              ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20 dark:border-blue-400'
              : 'border-gray-300 dark:border-gray-600 hover:border-gray-400 dark:hover:border-gray-500 hover:bg-gray-50 dark:hover:bg-gray-800/50'
          }`}
        >
          <input {...getInputProps()} />
          <Upload className="w-12 h-12 text-gray-400 dark:text-gray-500 mx-auto mb-4" />
          <h3 className="text-lg font-semibold mb-2 dark:text-white">
            {isDragActive ? 'Drop your resume here' : 'Drag & drop your resume'}
          </h3>
          <p className="text-gray-600 dark:text-gray-300 mb-4">
            or <span className="text-blue-600 dark:text-blue-400 font-medium">browse files</span>
          </p>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Supports PDF, DOC, DOCX, TXT • Max file size: 10MB
          </p>
        </div>
      ) : (
        // File Preview & Upload
        <div className="space-y-6">
          {/* File Info */}
          <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
            <div className="flex items-start gap-4">
              <div className="flex-shrink-0">
                <FileText className="w-10 h-10 text-blue-600" />
              </div>
              <div className="flex-1 min-w-0">
                <h3 className="font-medium truncate">{uploadState.file.name}</h3>
                <p className="text-sm text-gray-500">
                  {formatFileSize(uploadState.file.size)} • {uploadState.file.type}
                </p>
              </div>
              {!uploadState.uploading && !uploadState.success && (
                <button
                  onClick={handleRemoveFile}
                  className="flex-shrink-0 p-1 hover:bg-gray-100 rounded"
                >
                  <X className="w-4 h-4 text-gray-500" />
                </button>
              )}
            </div>

            {/* Progress Bar */}
            {uploadState.uploading && (
              <div className="mt-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-gray-600 dark:text-gray-300">Uploading...</span>
                  <span className="text-sm text-gray-600 dark:text-gray-300">{uploadState.progress}%</span>
                </div>
                <Progress value={uploadState.progress} className="h-2" />
              </div>
            )}

            {/* Success State */}
            {uploadState.success && (
              <div className="mt-4 flex items-center gap-2 text-green-600">
                <CheckCircle className="w-4 h-4" />
                <span className="text-sm font-medium">Upload successful!</span>
              </div>
            )}

            {/* Error State */}
            {uploadState.error && (
              <div className="mt-4 flex items-center gap-2 text-red-600">
                <AlertCircle className="w-4 h-4" />
                <span className="text-sm">{uploadState.error}</span>
              </div>
            )}
          </div>

          {/* Extracted Text Preview */}
          {uploadState.extractedText && (
            <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
              <h4 className="font-medium mb-2">Text Extraction Preview</h4>
              <div className="text-sm text-gray-700 max-h-32 overflow-y-auto">
                {uploadState.extractedText.substring(0, 500)}
                {uploadState.extractedText.length > 500 && '...'}
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex gap-3">
            {!uploadState.success && (
              <>
                <Button
                  onClick={handleUpload}
                  disabled={uploadState.uploading}
                  className="flex-1"
                >
                  {uploadState.uploading ? 'Uploading...' : 'Upload Resume'}
                </Button>
                {onCancel && (
                  <Button variant="outline" onClick={onCancel}>
                    Cancel
                  </Button>
                )}
              </>
            )}
            {uploadState.success && onCancel && (
              <Button onClick={onCancel} className="flex-1">
                Continue
              </Button>
            )}
          </div>
        </div>
      )}
    </div>
  );
}