import { useNavigate } from "react-router-dom"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { getRandomAccentColor } from "@/scripts/utils";
import { CircleUserRound, Settings } from "lucide-react";
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

export default function UserAvatar(user) {
    const navigate = useNavigate();

    function extractAvatarFallback() {
        const username = user["user"];
        if (!username) {
            return "USER"
        } else {
            const usernameStr = String(username);
            return usernameStr[0].toUpperCase();
        }

    }
    return (
        <DropdownMenu>
            <DropdownMenuTrigger asChild>
                <Avatar size="lg" className="cursor-pointer">
                    <AvatarImage src="TODO" />
                    <AvatarFallback className="font-semibold" style={{ backgroundColor: getRandomAccentColor() }}>{
                        extractAvatarFallback()}
                    </AvatarFallback>
                </Avatar>
            </DropdownMenuTrigger>
            <DropdownMenuContent>
                <DropdownMenuItem onClick={() => navigate(`/user/${user.user}`)}>
                    <CircleUserRound />
                    Profile
                </DropdownMenuItem>
                <DropdownMenuItem>
                    <Settings />
                    Settings
                </DropdownMenuItem>
            </DropdownMenuContent>
        </DropdownMenu>

    )
}