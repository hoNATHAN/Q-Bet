"use client"

import type React from "react"

import { useState, useMemo } from "react"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import {
  Pagination,
  PaginationContent,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from "@/components/ui/pagination"
import { ChevronDown, ChevronUp, ExternalLink, Search } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { formatDate } from "@/lib/utils"

// Define the keys for the table columns
export const keys = [
  "match_id",
  "tournament",
  "team_a",
  "team_b",
  "stage",
  "start_time",
  "status",
  "winner",
  "game_count",
  "link",
  "game_num",
]

// Define the match data type
interface Match {
  match_id: string
  tournament: string
  team_a: string
  team_b: string
  stage: string
  start_time: string
  status: string
  winner: string
  game_count: number
  link: string
  game_num: number
}

interface MatchTableProps {
  data: Match[]
}

export function MatchTable({ data }: MatchTableProps) {
  // State for search, filters, sorting, and pagination
  const [searchTerm, setSearchTerm] = useState("")
  const [filters, setFilters] = useState<Record<string, string>>({})
  const [sortConfig, setSortConfig] = useState<{
    key: string
    direction: "asc" | "desc"
  }>({ key: "start_time", direction: "desc" })
  const [currentPage, setCurrentPage] = useState(1)
  const itemsPerPage = 10

  // Get unique values for filter dropdowns
  const filterOptions = useMemo(() => {
    const options: Record<string, Set<string>> = {}

    // Only create filters for these categorical fields
    const filterableFields = ["tournament", "stage", "status"]

    filterableFields.forEach((field) => {
      options[field] = new Set(data.map((item) => item[field as keyof Match] as string))
    })

    return options
  }, [data])

  // Apply search filter
  const searchedData = useMemo(() => {
    if (!searchTerm) return data

    return data.filter((item) =>
      keys.some((key) => {
        const value = item[key as keyof Match]
        return value !== undefined && value.toString().toLowerCase().includes(searchTerm.toLowerCase())
      }),
    )
  }, [data, searchTerm])

  // Apply column filters
  const filteredData = useMemo(() => {
    return searchedData.filter((item) => {
      return Object.entries(filters).every(([key, value]) => {
        if (!value) return true
        return item[key as keyof Match]?.toString() === value
      })
    })
  }, [searchedData, filters])

  // Apply sorting
  const sortedData = useMemo(() => {
    const sorted = [...filteredData]

    sorted.sort((a, b) => {
      const aValue = a[sortConfig.key as keyof Match]
      const bValue = b[sortConfig.key as keyof Match]

      if (aValue === undefined || bValue === undefined) return 0

      // Handle date sorting
      if (sortConfig.key === "start_time") {
        return sortConfig.direction === "asc"
          ? new Date(aValue as string).getTime() - new Date(bValue as string).getTime()
          : new Date(bValue as string).getTime() - new Date(aValue as string).getTime()
      }

      // Handle numeric sorting
      if (typeof aValue === "number" && typeof bValue === "number") {
        return sortConfig.direction === "asc" ? aValue - bValue : bValue - aValue
      }

      // Handle string sorting
      return sortConfig.direction === "asc"
        ? String(aValue).localeCompare(String(bValue))
        : String(bValue).localeCompare(String(aValue))
    })

    return sorted
  }, [filteredData, sortConfig])

  // Apply pagination
  const paginatedData = useMemo(() => {
    const startIndex = (currentPage - 1) * itemsPerPage
    return sortedData.slice(startIndex, startIndex + itemsPerPage)
  }, [sortedData, currentPage])

  // Calculate total pages
  const totalPages = Math.ceil(sortedData.length / itemsPerPage)

  // Handle sort click
  const handleSort = (key: string) => {
    setSortConfig((prevConfig) => ({
      key,
      direction: prevConfig.key === key && prevConfig.direction === "asc" ? "desc" : "asc",
    }))
  }

  // Handle filter change
  const handleFilterChange = (key: string, value: string) => {
    setFilters((prev) => ({
      ...prev,
      [key]: value,
    }))
    setCurrentPage(1) // Reset to first page when filter changes
  }

  // Handle search change
  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(e.target.value)
    setCurrentPage(1) // Reset to first page when search changes
  }

  // Generate pagination items
  const paginationItems = () => {
    const items = []
    const maxVisiblePages = 5

    let startPage = Math.max(1, currentPage - Math.floor(maxVisiblePages / 2))
    const endPage = Math.min(totalPages, startPage + maxVisiblePages - 1)

    if (endPage - startPage + 1 < maxVisiblePages) {
      startPage = Math.max(1, endPage - maxVisiblePages + 1)
    }

    for (let i = startPage; i <= endPage; i++) {
      items.push(
        <PaginationItem key={i}>
          <PaginationLink isActive={currentPage === i} onClick={() => setCurrentPage(i)}>
            {i}
          </PaginationLink>
        </PaginationItem>,
      )
    }

    return items
  }

  // Render status badge with appropriate color
  const renderStatusBadge = (status: string) => {
    let variant: "default" | "outline" | "secondary" | "destructive" | "success" = "default"

    switch (status.toLowerCase()) {
      case "live":
        variant = "success"
        break
      case "upcoming":
        variant = "secondary"
        break
      case "ended":
        variant = "outline"
        break
      case "cancelled":
        variant = "destructive"
        break
    }

    return <Badge variant={variant}>{status}</Badge>
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        {/* Search */}
        <div className="relative w-full md:w-64">
          <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input placeholder="Search matches..." className="pl-8" value={searchTerm} onChange={handleSearchChange} />
        </div>

        {/* Filters */}
        <div className="flex flex-wrap gap-2">
          {Object.entries(filterOptions).map(([key, values]) => (
            <Select key={key} value={filters[key] || ""} onValueChange={(value) => handleFilterChange(key, value)}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder={`Filter by ${key}`} />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All {key}s</SelectItem>
                {Array.from(values).map((value) => (
                  <SelectItem key={value} value={value}>
                    {value}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          ))}

          {Object.keys(filters).length > 0 && (
            <Button
              variant="outline"
              onClick={() => {
                setFilters({})
                setCurrentPage(1)
              }}
              size="sm"
            >
              Clear Filters
            </Button>
          )}
        </div>
      </div>

      {/* Results count */}
      <div className="text-sm text-muted-foreground">
        Showing {paginatedData.length} of {sortedData.length} results
      </div>

      {/* Table */}
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="cursor-pointer" onClick={() => handleSort("match_id")}>
                Match ID
                {sortConfig.key === "match_id" &&
                  (sortConfig.direction === "asc" ? (
                    <ChevronUp className="inline ml-1 h-4 w-4" />
                  ) : (
                    <ChevronDown className="inline ml-1 h-4 w-4" />
                  ))}
              </TableHead>
              <TableHead className="cursor-pointer" onClick={() => handleSort("tournament")}>
                Tournament
                {sortConfig.key === "tournament" &&
                  (sortConfig.direction === "asc" ? (
                    <ChevronUp className="inline ml-1 h-4 w-4" />
                  ) : (
                    <ChevronDown className="inline ml-1 h-4 w-4" />
                  ))}
              </TableHead>
              <TableHead className="cursor-pointer" onClick={() => handleSort("team_a")}>
                Team A
                {sortConfig.key === "team_a" &&
                  (sortConfig.direction === "asc" ? (
                    <ChevronUp className="inline ml-1 h-4 w-4" />
                  ) : (
                    <ChevronDown className="inline ml-1 h-4 w-4" />
                  ))}
              </TableHead>
              <TableHead className="cursor-pointer" onClick={() => handleSort("team_b")}>
                Team B
                {sortConfig.key === "team_b" &&
                  (sortConfig.direction === "asc" ? (
                    <ChevronUp className="inline ml-1 h-4 w-4" />
                  ) : (
                    <ChevronDown className="inline ml-1 h-4 w-4" />
                  ))}
              </TableHead>
              <TableHead className="cursor-pointer" onClick={() => handleSort("stage")}>
                Stage
                {sortConfig.key === "stage" &&
                  (sortConfig.direction === "asc" ? (
                    <ChevronUp className="inline ml-1 h-4 w-4" />
                  ) : (
                    <ChevronDown className="inline ml-1 h-4 w-4" />
                  ))}
              </TableHead>
              <TableHead className="cursor-pointer" onClick={() => handleSort("start_time")}>
                Start Time
                {sortConfig.key === "start_time" &&
                  (sortConfig.direction === "asc" ? (
                    <ChevronUp className="inline ml-1 h-4 w-4" />
                  ) : (
                    <ChevronDown className="inline ml-1 h-4 w-4" />
                  ))}
              </TableHead>
              <TableHead className="cursor-pointer" onClick={() => handleSort("status")}>
                Status
                {sortConfig.key === "status" &&
                  (sortConfig.direction === "asc" ? (
                    <ChevronUp className="inline ml-1 h-4 w-4" />
                  ) : (
                    <ChevronDown className="inline ml-1 h-4 w-4" />
                  ))}
              </TableHead>
              <TableHead className="cursor-pointer" onClick={() => handleSort("winner")}>
                Winner
                {sortConfig.key === "winner" &&
                  (sortConfig.direction === "asc" ? (
                    <ChevronUp className="inline ml-1 h-4 w-4" />
                  ) : (
                    <ChevronDown className="inline ml-1 h-4 w-4" />
                  ))}
              </TableHead>
              <TableHead className="cursor-pointer" onClick={() => handleSort("game_count")}>
                Games
                {sortConfig.key === "game_count" &&
                  (sortConfig.direction === "asc" ? (
                    <ChevronUp className="inline ml-1 h-4 w-4" />
                  ) : (
                    <ChevronDown className="inline ml-1 h-4 w-4" />
                  ))}
              </TableHead>
              <TableHead className="cursor-pointer" onClick={() => handleSort("game_num")}>
                Game #
                {sortConfig.key === "game_num" &&
                  (sortConfig.direction === "asc" ? (
                    <ChevronUp className="inline ml-1 h-4 w-4" />
                  ) : (
                    <ChevronDown className="inline ml-1 h-4 w-4" />
                  ))}
              </TableHead>
              <TableHead>Link</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {paginatedData.length > 0 ? (
              paginatedData.map((match) => (
                <TableRow key={`${match.match_id}-${match.game_num}`}>
                  <TableCell className="font-medium">{match.match_id}</TableCell>
                  <TableCell>{match.tournament}</TableCell>
                  <TableCell>{match.team_a}</TableCell>
                  <TableCell>{match.team_b}</TableCell>
                  <TableCell>{match.stage}</TableCell>
                  <TableCell>{formatDate(match.start_time)}</TableCell>
                  <TableCell>{renderStatusBadge(match.status)}</TableCell>
                  <TableCell>{match.winner}</TableCell>
                  <TableCell>{match.game_count}</TableCell>
                  <TableCell>{match.game_num}</TableCell>
                  <TableCell>
                    <a
                      href={match.link}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center text-blue-600 hover:text-blue-800"
                    >
                      View <ExternalLink className="ml-1 h-3 w-3" />
                    </a>
                  </TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={11} className="h-24 text-center">
                  No results found.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <Pagination>
          <PaginationContent>
            <PaginationItem>
              <PaginationPrevious
                onClick={() => setCurrentPage((prev) => Math.max(1, prev - 1))}
                isActive={currentPage > 1}
              />
            </PaginationItem>

            {paginationItems()}

            <PaginationItem>
              <PaginationNext
                onClick={() => setCurrentPage((prev) => Math.min(totalPages, prev + 1))}
                isActive={currentPage < totalPages}
              />
            </PaginationItem>
          </PaginationContent>
        </Pagination>
      )}
    </div>
  )
}
