import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";

const Help = () => {
  return (
    <div>

      <Card className="p-4 mb-4">
      <h2 className="text-2xl font-semibold mb-4">Help & Support</h2>
        <p className="text-muted-foreground mt-1">
          Get assistance, FAQs, and troubleshooting guides.
        </p>
        {/* <h3 className="font-semibold">Documentation</h3>
        <p className="text-sm text-muted-foreground mt-2">
          Browse getting started guides, FAQs, and best practices for using
          the AI Hiring platform.
        </p>
        <div className="mt-3">
          <Button onClick={() => alert('Open docs')}>Open Documentation</Button>
        </div> */}
      </Card>

          {/*subject must not be empty*/}
          
      <Card className="p-4 mb-4">
        <h3 className="font-semibold">Contact Support</h3>
        <p className="text-sm text-muted-foreground mt-1">Submit a ticket</p>
        <div className="mt-3 grid grid-cols-1 gap-3">
          <Input placeholder="Subject" />
          <Textarea placeholder="Describe your issue" />
          <div className="flex justify-end">
            <Button onClick={() => alert('Ticket submitted')}>Send</Button>
          </div>
        </div>
      </Card>

      <Card className="p-4">
  <h3 className="text-lg font-semibold">Frequently Asked Questions</h3>

  <Accordion type="single" collapsible className="mt-4">
    <AccordionItem value="faq-1">
      <AccordionTrigger className="hover:no-underline">
        How do I adjust AI scoring weights?
      </AccordionTrigger>
      <AccordionContent>
        Go to Settings → AI Algorithm Preferences and adjust Resume,
        Assessment and Interview score weights. Make sure the total equals 100%.
      </AccordionContent>
    </AccordionItem>

    <AccordionItem value="faq-2">
      <AccordionTrigger className="hover:no-underline">
        How do I invite team members?
      </AccordionTrigger>
      <AccordionContent>
        Go to the Team section and click "Invite Members". Enter their email
        and assign roles such as Admin or Reviewer.
      </AccordionContent>
    </AccordionItem>

    <AccordionItem value="faq-3">
      <AccordionTrigger className="hover:no-underline">
        How are AI scores computed?
      </AccordionTrigger>
      <AccordionContent>
        AI calculates weighted performance from Resume, Assessment, and AI
        Interview results. We use NLP ranking, semantic scoring and ML scoring models.
      </AccordionContent>
    </AccordionItem>
  </Accordion>
</Card>
    </div>
  );
};

export default Help;
