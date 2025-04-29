REGISTER_HTML_CODE = """
<html>
  <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; margin: 0; padding: 0;">
    <table width="100%" cellspacing="0" cellpadding="0">
      <tr>
        <td align="center" style="padding: 40px 0;">
          <table width="600" style="background: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
            <tr>
              <td align="center" style="padding-bottom: 20px;">
                <h1 style="color: #333;">Welcome to HoldMyBeer!</h1>
              </td>
            </tr>
            <tr>
              <td style="font-size: 16px; color: #555; padding-bottom: 30px;">
                Thank you for signing up. Please verify your email address by entering the following 6-digit code:
              </td>
            </tr>
            <tr>
              <td align="center" style="padding-bottom: 30px;">
                <div style="display: inline-block; padding: 15px 30px; font-size: 24px; font-weight: bold; color: #4CAF50; background-color: #e8f5e9; border-radius: 8px; letter-spacing: 8px;">
                  {{CODE}}
                </div>
              </td>
            </tr>
            <tr>
              <td style="font-size: 14px; color: #999;">
                This code will expire in 15 minutes.
              </td>
            </tr>
            <tr>
              <td style="font-size: 12px; color: #bbb; padding-top: 20px;">
                If you did not create an account, you can safely ignore this email.
              </td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
  </body>
</html>
"""
RESET_PASSWORD_HTML_CODE = """
"""