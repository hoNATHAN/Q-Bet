import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Label } from "@/components/ui/label"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Progress } from "@/components/ui/progress"

export function Train() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Training Center</CardTitle>
        <CardDescription>Improve your skills with training exercises</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <Tabs defaultValue="skills">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="skills">Skills</TabsTrigger>
            <TabsTrigger value="drills">Drills</TabsTrigger>
            <TabsTrigger value="scenarios">Scenarios</TabsTrigger>
          </TabsList>

          <TabsContent value="skills" className="space-y-4 pt-4">
            <div className="space-y-2">
              <div className="flex justify-between">
                <Label>Accuracy</Label>
                <span className="text-sm text-muted-foreground">Level 3</span>
              </div>
              <Progress value={60} />
              <Button size="sm" className="w-full mt-2">
                Train Accuracy
              </Button>
            </div>

            <div className="space-y-2">
              <div className="flex justify-between">
                <Label>Speed</Label>
                <span className="text-sm text-muted-foreground">Level 2</span>
              </div>
              <Progress value={40} />
              <Button size="sm" className="w-full mt-2">
                Train Speed
              </Button>
            </div>

            <div className="space-y-2">
              <div className="flex justify-between">
                <Label>Strategy</Label>
                <span className="text-sm text-muted-foreground">Level 4</span>
              </div>
              <Progress value={80} />
              <Button size="sm" className="w-full mt-2">
                Train Strategy
              </Button>
            </div>
          </TabsContent>

          <TabsContent value="drills" className="space-y-4 pt-4">
            <div className="space-y-2">
              <Label htmlFor="drill-type">Select Drill Type</Label>
              <Select>
                <SelectTrigger id="drill-type">
                  <SelectValue placeholder="Select drill type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="reflex">Reflex Training</SelectItem>
                  <SelectItem value="aim">Aim Training</SelectItem>
                  <SelectItem value="movement">Movement Training</SelectItem>
                  <SelectItem value="combo">Combo Training</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="difficulty">Difficulty</Label>
              <Select>
                <SelectTrigger id="difficulty">
                  <SelectValue placeholder="Select difficulty" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="beginner">Beginner</SelectItem>
                  <SelectItem value="intermediate">Intermediate</SelectItem>
                  <SelectItem value="advanced">Advanced</SelectItem>
                  <SelectItem value="expert">Expert</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <Button className="w-full mt-4">Start Drill</Button>
          </TabsContent>

          <TabsContent value="scenarios" className="space-y-4 pt-4">
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <Card>
                <CardHeader className="p-4">
                  <CardTitle className="text-base">Defensive Play</CardTitle>
                </CardHeader>
                <CardFooter className="p-4 pt-0">
                  <Button size="sm" className="w-full">
                    Start
                  </Button>
                </CardFooter>
              </Card>

              <Card>
                <CardHeader className="p-4">
                  <CardTitle className="text-base">Offensive Play</CardTitle>
                </CardHeader>
                <CardFooter className="p-4 pt-0">
                  <Button size="sm" className="w-full">
                    Start
                  </Button>
                </CardFooter>
              </Card>

              <Card>
                <CardHeader className="p-4">
                  <CardTitle className="text-base">Resource Management</CardTitle>
                </CardHeader>
                <CardFooter className="p-4 pt-0">
                  <Button size="sm" className="w-full">
                    Start
                  </Button>
                </CardFooter>
              </Card>

              <Card>
                <CardHeader className="p-4">
                  <CardTitle className="text-base">Team Coordination</CardTitle>
                </CardHeader>
                <CardFooter className="p-4 pt-0">
                  <Button size="sm" className="w-full">
                    Start
                  </Button>
                </CardFooter>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
      <CardFooter className="flex justify-between">
        <Button variant="outline">View Progress</Button>
        <Button>Training History</Button>
      </CardFooter>
    </Card>
  )
}
