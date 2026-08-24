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
import VerifyEmail from "./SettingsTabs/VerifyEmail"
import InformationTab from "./SettingsTabs/InformationTab"
import ChangePassword from "./SettingsTabs/ChangePassword"


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
                        <TabsTrigger value="verifyEmail">Verify e-mail</TabsTrigger>
                        <TabsTrigger value="changePassword">Change Password</TabsTrigger>
                        <TabsTrigger value="info">Information</TabsTrigger>
                    </TabsList>

                    <TabsContent value="verifyEmail">
                        <VerifyEmail />
                    </TabsContent>

                    <TabsContent value="changePassword">
                        <ChangePassword />
                    </TabsContent>

                    <TabsContent value="info">
                        <InformationTab />
                    </TabsContent>
                </Tabs>
            </DialogContent>
        </Dialog>
    )
}