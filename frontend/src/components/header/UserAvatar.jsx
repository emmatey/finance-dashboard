import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { getRandomAccentColor } from "@/scripts/utils";

export default function UserAvatar(user) {
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
       <Avatar size="lg">
            <AvatarImage src="TODO"/>
            <AvatarFallback className="font-semibold" style={{ backgroundColor: getRandomAccentColor() }}>{
                extractAvatarFallback()}
            </AvatarFallback>
       </Avatar>
    )
}