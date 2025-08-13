"use client"
import { Button } from "@/components/ui/button"
import {
  Card,
  // CardAction,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

import useAlertData from "./hooks/useAlertData"

import styled from "styled-components"

import { AlertCard } from "@/components/ui/AlertCard"

const AlertGrid = styled.div`
  padding: 20px;
  display: flex;
  flex-wrap: wrap;
  align-content: center;
  align-items: center;
`;

const AlertGridClosed = styled.div`
  background: red;
  padding: 20px;
  display: flex;
  flex-wrap: wrap;
  align-content: center;
`;

type Alert = { id: number; alert_name: string };

export default function Home() {

  const {openAlerts, closedAlerts, markResolved} = useAlertData()  as {
    openAlerts: Alert[];
    closedAlerts: Alert[];
    markResolved: (id: number) => void;
  };

  return (
    <div>
    <AlertGrid>
      {
        openAlerts && openAlerts.map(alert =>
          <AlertCard id={alert.id} alert_name={alert.alert_name} markResolved={markResolved}/>
        )
      }
    </AlertGrid>
    <AlertGridClosed>
    {
      closedAlerts && closedAlerts.map(alert =>
        <AlertCard id={alert?.id} alert_name={alert.alert_name}/>
      )
    }
  </AlertGridClosed>
  </div>
  )
}


