// This class is used to send outgoing plaintext emails.
public class EmailUtility {
    
    // Send an email to the address passed in
    public static void sendMail(String address, String subject, String body) {
       
        // Create an email message object
        Messaging.SingleEmailMessage mail = new Messaging.SingleEmailMessage();
        
        // SingleEmailMessage methods require a list of addresses
        String[] toAddresses = new String[] {address};
        
		// Set email attributes
        mail.setToAddresses(toAddresses);
        mail.setSubject(subject);
        mail.setPlainTextBody(body);
       
        // Pass the prepared email message to the builtin sendEmail method of
        // Messaging class
        Messaging.SendEmailResult[] results = Messaging.sendEmail(
                                 new Messaging.SingleEmailMessage[] { mail });
        
        // Call a method for inspecting the returned results
        inspectResults(results);
    }
    
    // Helper method to inspect only email sending return results
    private static Boolean inspectResults(Messaging.SendEmailResult[] results) {
        Boolean sendResult = true;
        
        // sendEmail returns an array of result objects
        for (Messaging.SendEmailResult res : results) {
            if (res.isSuccess()) {
                System.debug('Email sent successfully');
            }
            else {
                sendResult = false;
                System.debug('The following errors occurred: ' + res.getErrors());                 
            }
        }
        
        return sendResult;
    }
}