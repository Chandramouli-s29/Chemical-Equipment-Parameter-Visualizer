import { useState, useEffect } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Button } from '@/components/ui/button';
import { Loader2, ChevronLeft, ChevronRight } from 'lucide-react';
import { api } from '@/lib/api';
import type { EquipmentItem } from '@/lib/api';
import { toast } from 'sonner';

interface DataTableProps {
  datasetId: number;
}

export function DataTable({ datasetId }: DataTableProps) {
  const [items, setItems] = useState<EquipmentItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;

  useEffect(() => {
    fetchItems();
  }, [datasetId]);

  const fetchItems = async () => {
    setIsLoading(true);
    try {
      const data = await api.getItems(datasetId);
      setItems(data);
    } catch (error) {
      toast.error('Failed to load equipment data');
    } finally {
      setIsLoading(false);
    }
  };

  const totalPages = Math.ceil(items.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const paginatedItems = items.slice(startIndex, startIndex + itemsPerPage);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow className="bg-slate-50">
              <TableHead className="font-semibold">Equipment Name</TableHead>
              <TableHead className="font-semibold">Type</TableHead>
              <TableHead className="font-semibold text-right">Flowrate</TableHead>
              <TableHead className="font-semibold text-right">Pressure</TableHead>
              <TableHead className="font-semibold text-right">Temperature</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {paginatedItems.map((item) => (
              <TableRow key={item.id} className="hover:bg-slate-50">
                <TableCell className="font-medium">{item.equipment_name}</TableCell>
                <TableCell>
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                    {item.equipment_type}
                  </span>
                </TableCell>
                <TableCell className="text-right">
                  {item.flowrate !== null ? (
                    <span className="font-mono">{item.flowrate.toFixed(2)}</span>
                  ) : (
                    <span className="text-slate-400">-</span>
                  )}
                </TableCell>
                <TableCell className="text-right">
                  {item.pressure !== null ? (
                    <span className="font-mono">{item.pressure.toFixed(2)}</span>
                  ) : (
                    <span className="text-slate-400">-</span>
                  )}
                </TableCell>
                <TableCell className="text-right">
                  {item.temperature !== null ? (
                    <span className="font-mono">{item.temperature.toFixed(2)}</span>
                  ) : (
                    <span className="text-slate-400">-</span>
                  )}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between">
          <p className="text-sm text-slate-500">
            Showing {startIndex + 1} to {Math.min(startIndex + itemsPerPage, items.length)} of{' '}
            {items.length} entries
          </p>
          <div className="flex items-center space-x-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
              disabled={currentPage === 1}
            >
              <ChevronLeft className="h-4 w-4" />
            </Button>
            <span className="text-sm text-slate-600">
              Page {currentPage} of {totalPages}
            </span>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
              disabled={currentPage === totalPages}
            >
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
