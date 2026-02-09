import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Calendar, 
  FileText, 
  ChevronRight, 
  Trash2, 
  Loader2,
  Database
} from 'lucide-react';
import { api } from '@/lib/api';
import type { Dataset } from '@/lib/api';
import { toast } from 'sonner';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/alert-dialog';

interface HistoryViewProps {
  datasets: Dataset[];
  onSelect: (dataset: Dataset) => void;
  isLoading: boolean;
}

export function HistoryView({ datasets, onSelect, isLoading }: HistoryViewProps) {
  const [deletingId, setDeletingId] = useState<number | null>(null);

  const handleDelete = async (id: number) => {
    setDeletingId(id);
    try {
      await api.deleteDataset(id);
      toast.success('Dataset deleted');
      window.location.reload();
    } catch (error) {
      toast.error('Failed to delete dataset');
    } finally {
      setDeletingId(null);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (isLoading) {
    return (
      <Card>
        <CardContent className="p-12">
          <div className="flex items-center justify-center">
            <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
          </div>
        </CardContent>
      </Card>
    );
  }

  if (datasets.length === 0) {
    return (
      <Card>
        <CardContent className="p-12">
          <div className="text-center space-y-4">
            <div className="bg-slate-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto">
              <Database className="h-8 w-8 text-slate-400" />
            </div>
            <div>
              <h3 className="text-lg font-medium text-slate-900">No datasets yet</h3>
              <p className="text-slate-500 mt-1">
                Upload a CSV file to get started with your equipment data analysis
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Database className="h-5 w-5 text-blue-500" />
            Recent Datasets ({datasets.length}/5)
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {datasets.map((dataset, index) => (
            <div
              key={dataset.id}
              className="group flex items-center justify-between p-4 rounded-lg border border-slate-200 hover:border-blue-300 hover:bg-blue-50/50 transition-all cursor-pointer"
              onClick={() => onSelect(dataset)}
            >
              <div className="flex items-center space-x-4">
                <div className="bg-blue-100 p-3 rounded-lg">
                  <FileText className="h-5 w-5 text-blue-600" />
                </div>
                <div>
                  <h4 className="font-medium text-slate-900">{dataset.name}</h4>
                  <div className="flex items-center space-x-3 mt-1">
                    <span className="flex items-center text-sm text-slate-500">
                      <Calendar className="h-3.5 w-3.5 mr-1" />
                      {formatDate(dataset.uploaded_at)}
                    </span>
                    <Badge variant="secondary" className="text-xs">
                      {dataset.item_count} items
                    </Badge>
                    {index === 0 && (
                      <Badge className="bg-green-100 text-green-700 text-xs">
                        Latest
                      </Badge>
                    )}
                  </div>
                </div>
              </div>
              
              <div className="flex items-center space-x-2">
                <Button 
                  variant="ghost" 
                  size="sm"
                  className="opacity-0 group-hover:opacity-100 transition-opacity"
                  onClick={(e) => {
                    e.stopPropagation();
                    onSelect(dataset);
                  }}
                >
                  View
                  <ChevronRight className="h-4 w-4 ml-1" />
                </Button>
                
                <AlertDialog>
                  <AlertDialogTrigger asChild>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="text-red-500 hover:text-red-600 hover:bg-red-50 opacity-0 group-hover:opacity-100 transition-opacity"
                      onClick={(e) => e.stopPropagation()}
                    >
                      {deletingId === dataset.id ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        <Trash2 className="h-4 w-4" />
                      )}
                    </Button>
                  </AlertDialogTrigger>
                  <AlertDialogContent>
                    <AlertDialogHeader>
                      <AlertDialogTitle>Delete Dataset</AlertDialogTitle>
                      <AlertDialogDescription>
                        Are you sure you want to delete "{dataset.name}"? This action cannot be undone.
                      </AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter>
                      <AlertDialogCancel>Cancel</AlertDialogCancel>
                      <AlertDialogAction
                        onClick={() => handleDelete(dataset.id)}
                        className="bg-red-500 hover:bg-red-600"
                      >
                        Delete
                      </AlertDialogAction>
                    </AlertDialogFooter>
                  </AlertDialogContent>
                </AlertDialog>
              </div>
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Info Card */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <p className="text-sm text-blue-700">
          <strong>Note:</strong> Only the last 5 datasets are kept. Older datasets are automatically deleted when new ones are uploaded.
        </p>
      </div>
    </div>
  );
}
