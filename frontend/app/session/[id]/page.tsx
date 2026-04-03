import { redirect } from "next/navigation";

// Direct session URL → send to questionnaire
export default function SessionPage({ params }: { params: { id: string } }) {
  redirect(`/session/${params.id}/questionnaire`);
}
