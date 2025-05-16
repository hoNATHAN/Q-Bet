import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Slider } from "@/components/ui/slider"
import { Switch } from "@/components/ui/switch"
import { Label } from "@/components/ui/label"

export function RunMatch() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Run Match</CardTitle>
        <CardDescription>Configure and start a new match</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="space-y-2">
          <Label htmlFor="opponent">Select Opponent</Label>
          <Select>
            <SelectTrigger id="opponent">
              <SelectValue placeholder="Select opponent" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="ai-easy">AI (Easy)</SelectItem>
              <SelectItem value="ai-medium">AI (Medium)</SelectItem>
              <SelectItem value="ai-hard">AI (Hard)</SelectItem>
              <SelectItem value="player">Another Player</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <Label htmlFor="map">Select Map</Label>
          <Select>
            <SelectTrigger id="map">
              <SelectValue placeholder="Select map" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="map1">Arena</SelectItem>
              <SelectItem value="map2">Forest</SelectItem>
              <SelectItem value="map3">Desert</SelectItem>
              <SelectItem value="map4">Mountain</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <div className="flex justify-between">
            <Label htmlFor="time-limit">Time Limit (minutes)</Label>
            <span className="text-sm text-muted-foreground">10</span>
          </div>
          <Slider id="time-limit" defaultValue={[10]} max={30} min={1} step={1} />
        </div>

        <div className="flex items-center justify-between">
          <Label htmlFor="spectators" className="cursor-pointer">
            Allow Spectators
          </Label>
          <Switch id="spectators" />
        </div>
      </CardContent>
      <CardFooter>
        <Button className="w-full">Start Match</Button>
      </CardFooter>
    </Card>
  )
}
