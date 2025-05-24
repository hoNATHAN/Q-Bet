'use client';
import { useState } from 'react';
import {
  CaretSortIcon,
  ChevronDownIcon,
  DotsHorizontalIcon,
} from '@radix-ui/react-icons';
import {
  type ColumnDef,
  type ColumnFiltersState,
  type SortingState,
  type VisibilityState,
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  useReactTable,
} from '@tanstack/react-table';

import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
import {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Input } from '@/components/ui/input';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { format } from 'date-fns';

interface Match {
  _id: string;
  tournament: string;
  team_a: string;
  team_b: string;
  stage: string;
  start_time: string;
  status: string;
  winner: string;
  game_count: number;
  link: string;
  game_num: number;
}

const matches: Match[] = [
  {
    _id: 'navi-vs-faze-15-10-2023',
    tournament: 'ESL Pro League Season 18',
    team_a: 'Natus Vincere',
    team_b: 'FaZe Clan',
    stage: 'Quarterfinals',
    start_time: '2023-10-15T18:00:00Z',
    status: 'Ended',
    winner: 'FaZe Clan',
    game_count: 3,
    link: 'https://esl.com/matches/navi-faze-1015',
    game_num: 1,
  },
  {
    _id: 'vitality-vs-g2-16-10-2023',
    tournament: 'ESL Pro League Season 18',
    team_a: 'Team Vitality',
    team_b: 'G2 Esports',
    stage: 'Semifinals',
    start_time: '2023-10-16T16:00:00Z',
    status: 'Ended',
    winner: 'Team Vitality',
    game_count: 3,
    link: 'https://esl.com/matches/vitality-g2-1016',
    game_num: 1,
  },
  {
    _id: 'liquid-vs-cloud9-14-10-2023',
    tournament: 'BLAST Premier Fall',
    team_a: 'Team Liquid',
    team_b: 'Cloud9',
    stage: 'Group Stage',
    start_time: '2023-10-14T20:00:00Z',
    status: 'Ended',
    winner: 'Team Liquid',
    game_count: 2,
    link: 'https://blast.com/matches/liquid-cloud9-1014',
    game_num: 1,
  },
  {
    _id: 'astralis-vs-nip-17-10-2023',
    tournament: 'BLAST Premier Fall',
    team_a: 'Astralis',
    team_b: 'Ninjas in Pyjamas',
    stage: 'Group Stage',
    start_time: '2023-10-17T19:00:00Z',
    status: 'Scheduled',
    winner: '',
    game_count: 3,
    link: 'https://blast.com/matches/astralis-nip-1017',
    game_num: 1,
  },
  {
    _id: 'faze-vs-vitality-18-10-2023',
    tournament: 'ESL Pro League Season 18',
    team_a: 'FaZe Clan',
    team_b: 'Team Vitality',
    stage: 'Finals',
    start_time: '2023-10-18T18:00:00Z',
    status: 'Scheduled',
    winner: '',
    game_count: 5,
    link: 'https://esl.com/matches/faze-vitality-1018',
    game_num: 1,
  },
];

const columns: ColumnDef<Match>[] = [
  {
    id: 'select',
    header: ({ table }) => (
      <Checkbox
        checked={
          table.getIsAllPageRowsSelected() ||
          (table.getIsSomePageRowsSelected() && 'indeterminate')
        }
        onCheckedChange={(value) => table.toggleAllPageRowsSelected(!!value)}
        aria-label="Select all"
      />
    ),
    cell: ({ row }) => (
      <Checkbox
        checked={row.getIsSelected()}
        onCheckedChange={(value) => row.toggleSelected(!!value)}
        aria-label="Select row"
      />
    ),
    enableSorting: false,
    enableHiding: false,
  },
  {
    accessorKey: 'tournament',
    header: 'Tournament',
    cell: ({ row }) => (
      <div className="font-medium">{row.getValue('tournament')}</div>
    ),
  },
  {
    accessorKey: 'team_a',
    header: 'Team A',
    cell: ({ row }) => <div>{row.getValue('team_a')}</div>,
  },
  {
    accessorKey: 'team_b',
    header: 'Team B',
    cell: ({ row }) => <div>{row.getValue('team_b')}</div>,
  },
  {
    accessorKey: 'stage',
    header: 'Stage',
    cell: ({ row }) => <div>{row.getValue('stage')}</div>,
  },
  {
    accessorKey: 'start_time',
    header: ({ column }) => {
      return (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
        >
          Date
          <CaretSortIcon className="ml-2 h-4 w-4" />
        </Button>
      );
    },
    cell: ({ row }) => {
      const startTime = new Date(row.getValue('start_time'));
      return <div>{format(startTime, 'PPP p')}</div>;
    },
  },
  {
    accessorKey: 'status',
    header: 'Status',
    cell: ({ row }) => {
      const status = row.getValue('status') as string;
      return (
        <Badge variant={status === 'Ended' ? 'outline' : 'default'}>
          {status}
        </Badge>
      );
    },
  },
  {
    accessorKey: 'winner',
    header: 'Winner',
    cell: ({ row }) => {
      const winner = row.getValue('winner') as string;
      return winner ? (
        <div>{winner}</div>
      ) : (
        <div className="text-muted-foreground">-</div>
      );
    },
  },
  {
    accessorKey: 'game_count',
    header: 'Games',
    cell: ({ row }) => (
      <div className="text-center">{row.getValue('game_count')}</div>
    ),
  },
  {
    id: 'actions',
    enableHiding: false,
    cell: ({ row }) => {
      const match = row.original;

      return (
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" className="h-8 w-8 p-0">
              <span className="sr-only">Open menu</span>
              <DotsHorizontalIcon className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuLabel>Actions</DropdownMenuLabel>
            <DropdownMenuItem
              onClick={() => navigator.clipboard.writeText(match._id)}
            >
              Copy match ID
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem>
              <a href={match.link} target="_blank" rel="noopener noreferrer">
                View match details
              </a>
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      );
    },
  },
];

export const MatchesTable = () => {
  const [sorting, setSorting] = useState<SortingState>([]);
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
  const [columnVisibility, setColumnVisibility] = useState<VisibilityState>({});
  const [rowSelection, setRowSelection] = useState({});
  const [globalFilter, setGlobalFilter] = useState('');

  const table = useReactTable({
    data: matches,
    columns,
    onSortingChange: setSorting,
    onColumnFiltersChange: setColumnFilters,
    onGlobalFilterChange: setGlobalFilter,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    onColumnVisibilityChange: setColumnVisibility,
    onRowSelectionChange: setRowSelection,
    state: {
      sorting,
      columnFilters,
      columnVisibility,
      rowSelection,
      globalFilter,
    },
  });

  const tournaments = [...new Set(matches.map((match) => match.tournament))];
  const stages = [...new Set(matches.map((match) => match.stage))];
  const statuses = [...new Set(matches.map((match) => match.status))];

  return (
    <div className="w-full">
      <div className="flex flex-col gap-4 py-4 md:flex-row md:items-center">
        <Input
          placeholder="Search matches..."
          value={globalFilter}
          onChange={(e) => setGlobalFilter(e.target.value)}
          className="max-w-sm"
        />
        <div className="flex flex-1 items-center space-x-2">
          <Select
            onValueChange={(value) =>
              table
                .getColumn('tournament')
                ?.setFilterValue(value === 'all' ? '' : value)
            }
          >
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="Tournament" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Tournaments</SelectItem>
              {tournaments.map((tournament) => (
                <SelectItem key={tournament} value={tournament}>
                  {tournament}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Select
            onValueChange={(value) =>
              table
                .getColumn('stage')
                ?.setFilterValue(value === 'all' ? '' : value)
            }
          >
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="Stage" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Stages</SelectItem>
              {stages.map((stage) => (
                <SelectItem key={stage} value={stage}>
                  {stage}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Select
            onValueChange={(value) =>
              table
                .getColumn('status')
                ?.setFilterValue(value === 'all' ? '' : value)
            }
          >
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="Status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Statuses</SelectItem>
              {statuses.map((status) => (
                <SelectItem key={status} value={status}>
                  {status}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <div className="ml-auto flex items-center space-x-2">
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" className="ml-auto">
                Columns <ChevronDownIcon className="ml-2 h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              {table
                .getAllColumns()
                .filter((column) => column.getCanHide())
                .map((column) => {
                  return (
                    <DropdownMenuCheckboxItem
                      key={column.id}
                      className="capitalize"
                      checked={column.getIsVisible()}
                      onCheckedChange={(value) =>
                        column.toggleVisibility(!!value)
                      }
                    >
                      {column.id}
                    </DropdownMenuCheckboxItem>
                  );
                })}
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            {table.getHeaderGroups().map((headerGroup) => (
              <TableRow key={headerGroup.id}>
                {headerGroup.headers.map((header) => {
                  return (
                    <TableHead key={header.id}>
                      {header.isPlaceholder
                        ? null
                        : flexRender(
                            header.column.columnDef.header,
                            header.getContext()
                          )}
                    </TableHead>
                  );
                })}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            {table.getRowModel().rows?.length ? (
              table.getRowModel().rows.map((row) => (
                <TableRow
                  key={row.id}
                  data-state={row.getIsSelected() && 'selected'}
                >
                  {row.getVisibleCells().map((cell) => (
                    <TableCell key={cell.id}>
                      {flexRender(
                        cell.column.columnDef.cell,
                        cell.getContext()
                      )}
                    </TableCell>
                  ))}
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell
                  colSpan={columns.length}
                  className="h-24 text-center"
                >
                  No results.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>
      <div className="flex items-center justify-end space-x-2 py-4">
        <div className="flex-1 text-sm text-muted-foreground">
          {table.getFilteredSelectedRowModel().rows.length} of{' '}
          {table.getFilteredRowModel().rows.length} row(s) selected.
        </div>
        <div className="space-x-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => table.previousPage()}
            disabled={!table.getCanPreviousPage()}
          >
            Previous
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => table.nextPage()}
            disabled={!table.getCanNextPage()}
          >
            Next
          </Button>
        </div>
      </div>
    </div>
  );
};
