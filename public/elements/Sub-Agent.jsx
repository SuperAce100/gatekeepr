import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";

export default function SubAgent() {
  // Check if agents exist in props
  if (!props.agents || !Array.isArray(props.agents) || props.agents.length === 0) {
    return <div className="text-muted-foreground italic">No sub-agents available</div>;
  }

  return (
    <Accordion type="single" collapsible className="w-full">
      {props.agents.map((agent, index) => (
        <AccordionItem key={index} value={`item-${index}`}>
          <AccordionTrigger className="font-medium">{agent.name}</AccordionTrigger>
          <AccordionContent>
            <div className="text-sm text-muted-foreground">{agent.description}</div>
          </AccordionContent>
        </AccordionItem>
      ))}
    </Accordion>
  );
}

