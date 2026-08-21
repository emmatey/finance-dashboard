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
import AccountSecurityTab from "./SettingsTabs/AccountSecurityTab"
import InformationTab from "./SettingsTabs/InformationTab"


export default function SettingsMenu({ open, onOpenChange }) {
    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent showCloseButton={true}>
                <DialogHeader>
                    <DialogTitle>
                        Settings Menu
                    </DialogTitle>
                </DialogHeader>
                <Tabs defaultValue="accountSecurity" orientation="vertical">
                    <TabsList>
                        <TabsTrigger value="accountSecurity">Account Security</TabsTrigger>
                        <TabsTrigger value="info">Information</TabsTrigger>
                    </TabsList>

                    <TabsContent value="accountSecurity">
                        <AccountSecurityTab />
                    </TabsContent>

                    <TabsContent value="info">
                        <InformationTab />
                    </TabsContent>
                </Tabs>
            </DialogContent>
        </Dialog>
    )
}