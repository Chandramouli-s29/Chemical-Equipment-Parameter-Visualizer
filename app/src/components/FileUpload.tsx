import { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Upload, File, X, Loader2 } from 'lucide-react';
import { toast } from 'sonner';

interface FileUploadProps {
  onUpload: (file: File, name: string) => void;
  isLoading: boolean;
}

export function FileUpload({ onUpload, isLoading }: FileUploadProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [datasetName, setDatasetName] = useState('');

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (file) {
      if (file.type === 'text/csv' || file.name.endsWith('.csv')) {
        setSelectedFile(file);
        setDatasetName(file.name.replace('.csv', ''));
      } else {
        toast.error('Please upload a CSV file');
      }
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
    },
    multiple: false,
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (selectedFile && datasetName) {
      onUpload(selectedFile, datasetName);
    }
  };

  const clearFile = () => {
    setSelectedFile(null);
    setDatasetName('');
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Dropzone */}
      <div
        {...getRootProps()}
        className={`
          border-2 border-dashed rounded-xl p-8 text-center cursor-pointer
          transition-colors duration-200
          ${isDragActive 
            ? 'border-blue-500 bg-blue-50' 
            : 'border-slate-300 hover:border-slate-400 hover:bg-slate-50'
          }
        `}
      >
        <input {...getInputProps()} />
        <Upload className="mx-auto h-12 w-12 text-slate-400 mb-4" />
        {isDragActive ? (
          <p className="text-blue-600 font-medium">Drop the CSV file here...</p>
        ) : (
          <>
            <p className="text-slate-700 font-medium mb-2">
              Drag & drop a CSV file here, or click to select
            </p>
            <p className="text-slate-500 text-sm">
              Supports CSV files with columns: Equipment Name, Type, Flowrate, Pressure, Temperature
            </p>
          </>
        )}
      </div>

      {/* Selected File */}
      {selectedFile && (
        <div className="bg-slate-50 rounded-lg p-4 border border-slate-200">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="bg-green-100 p-2 rounded-lg">
                <File className="h-5 w-5 text-green-600" />
              </div>
              <div>
                <p className="font-medium text-slate-900">{selectedFile.name}</p>
                <p className="text-sm text-slate-500">
                  {(selectedFile.size / 1024).toFixed(2)} KB
                </p>
              </div>
            </div>
            <button
              type="button"
              onClick={clearFile}
              className="text-slate-400 hover:text-red-500 transition-colors"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
        </div>
      )}

      {/* Dataset Name */}
      {selectedFile && (
        <div className="space-y-2">
          <Label htmlFor="datasetName" className="text-slate-700">
            Dataset Name
          </Label>
          <Input
            id="datasetName"
            type="text"
            placeholder="Enter a name for this dataset"
            value={datasetName}
            onChange={(e) => setDatasetName(e.target.value)}
            required
            className="h-11"
          />
        </div>
      )}

      {/* Submit Button */}
      {selectedFile && (
        <Button 
          type="submit" 
          className="w-full h-11"
          disabled={isLoading || !datasetName}
        >
          {isLoading ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Uploading...
            </>
          ) : (
            <>
              <Upload className="mr-2 h-4 w-4" />
              Upload & Analyze
            </>
          )}
        </Button>
      )}
    </form>
  );
}
