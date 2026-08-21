import {
    Dialog,
    DialogClose,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "@/components/ui/dialog"
import {
    Tabs,
    TabsContent,
    TabsList,
    TabsTrigger
} from "@/components/ui/tabs"
import { Button } from "../ui/button"


export default function SettingsMenu({open, onOpenChange}) {
    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
                <DialogContent showCloseButton={false}>
                    <p>TEST</p>
                </DialogContent>
        </Dialog>
    )
}