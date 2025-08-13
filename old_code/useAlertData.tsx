import { useCallback, useState } from "react"

type Alert = {
    id: number;
    alert_name: string;
}
export default function useAlertData() {
    const [openAlerts, setOpenAlerts]  = useState<Alert[]>([
        {"id": 1, "alert_name": "intrusion"},
        {"id": 2, "alert_name": "detection"},
        {"id": 3, "alert_name": "faulty"},
        {"id": 4, "alert_name": "tamper"},
    ]);

    const [closedAlerts, setClosedAlerts]  = useState<Alert[]>([]);

    const markResolved = useCallback((removeAlertId: number) => {
        const alertToRemove = openAlerts.find(alert => alert.id === removeAlertId);
        
        if (alertToRemove) {
            const updatedItems = openAlerts.filter(alert => alert.id !== removeAlertId);
            setOpenAlerts(updatedItems);
    
            setClosedAlerts([...closedAlerts, alertToRemove])
        }
    }, [openAlerts, closedAlerts]);


    return {openAlerts, closedAlerts, markResolved}
}