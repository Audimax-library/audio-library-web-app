from email.message import EmailMessage
import os
import ssl
import smtplib
from dotenv import load_dotenv

load_dotenv()
email_sender = os.getenv('Gmail')
email_password = os.getenv('Gmail-Password')
subject = 'Audimax NewsLetter'
body ='subscribed to newsLetter'

def send_mail(Reciver_email):
    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = Reciver_email
    em['Subject']= subject
    em.set_content(body)
    em.add_alternative("""
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">

<head>
    <meta name="robots" content="noindex, follow">
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <meta name="x-apple-disable-message-reformatting">
    <meta name="viewport" content="width=device-width,initial-scale=1,minimum-scale=1,maximum-scale=1">
    <title>Newsletter</title>
    <!--[if gte mso 9]>
        <style>
            .inner-row-table {
                border: none;
                width: 600px !important;
            }

            .newsletter-button-link, .text-element-td {
                font-family: Arial, sans-serif;
            }

            li {
                text-indent:-1em;
            }
        </style>
    <![endif]-->
    <!--[if (mso)|(mso 16)]>
        <style type="text/css">
            a {text-decoration: none;}
        </style>
    <![endif]-->
    <style>
        body {
            margin: 0 !important;
            padding: 0 !important
        }

        p {
            margin: 0
        }

        table {
            border-collapse: collapse;
            min-height: 0 !important
        }

        td {
            border-collapse: collapse;
            white-space: -moz-pre-wrap !important;
            white-space: -webkit-pre-wrap;
            white-space: -pre-wrap;
            white-space: -o-pre-wrap;
            white-space: pre-wrap;
            word-wrap: normal;
            word-break: normal;
            white-space: normal;
            border: none !important
        }

        .main-table,
        .newsletter-row {
            width: 100%
        }

        .component.text-component a {
            color: #337ab7;
            text-decoration: none !important
        }

        .component.text-component a:focus,
        .component.text-component a:hover {
            color: #23527c;
            text-decoration: underline;
            outline: 0
        }

        @media only screen and (max-width:700px) {
            #newsletter-tracking-image-id {
                display: none !important
            }

            .newsletter-tracking-image-class {
                display: none !important
            }
        }

        @media only screen and (max-width: 700px) {
            table {
                border-collapse: initial;
            }

            .component .image {
                mso-line-height-rule: exactly;
            }

            .component .newsletter-button-link .button {
                width: auto !important
            }

            .component,
            .image table {
                width: 100% !important
            }

            .responsive-row .inner-row-table .slot {
                width: 100% !important;
                max-width: 100% !important;
                display: block;
            }

            .responsive-row .inner-row-table .slot.ONE_FOURTH {
                width: 50% !important;
                max-width: 50% !important;
                display: inline-block
            }

            .non-responsive .slot.FULL {
                width: 100% !important;
                max-width: 100% !important;
            }

            .non-responsive .slot.ONE_THIRD {
                width: 33.3% !important;
                max-width: 33.3% !important;
            }

            .non-responsive .slot.HALF {
                width: 50% !important;
                max-width: 50% !important;
            }

            .non-responsive .slot.TWO_THIRDS {
                width: 66.6% !important;
                max-width: 66.6% !important;
            }

            .non-responsive .slot.ONE_FOURTH {
                width: 25% !important;
                max-width: 25% !important;
            }

            .fix-android-mail {
                /*remove width placeholder set due to Android 6.0 client*/
                display: none;
            }

            #bg_color_table {
                width: 100%
            }

            .slot-spacing {
                display: none
            }

            .non-responsive .slot-spacing {
                display: none;
            }

            .non-responsive .slot-spacing.CENTER {
                display: none;
            }

            .non-responsive .slot {
                display: table-cell;
            }

            .non-responsive .slot.FULL .image-component img {
                max-width: 100% !important
            }

            .non-responsive .slot.ONE_THIRD .image-component img {
                max-width: 100% !important
            }

            .non-responsive .slot.HALF .image-component img {
                max-width: 100% !important
            }

            .non-responsive .slot.TWO_THIRDS .image-component img {
                max-width: 100% !important
            }

            .non-responsive .slot.ONE_FOURTH .image-component img {
                max-width: 100% !important
            }

            .non-responsive .slot.FULL .product-component img {
                max-width: 100% !important
            }

            .non-responsive .slot.ONE_THIRD .product-component img {
                max-width: 100% !important
            }

            .non-responsive .slot.HALF .product-component img {
                max-width: 100% !important
            }

            .non-responsive .slot.TWO_THIRDS .product-component img {
                max-width: 100% !important
            }

            .non-responsive .slot.ONE_FOURTH .product-component img {
                max-width: 100% !important
            }

            .component .image img {
                max-width: 100% !important
            }

            .slot.HALF .image img.not-resized {
                max-width: 100% !important;
                width: 100% !important;
            }

            .slot.ONE_THIRD .image img.not-resized {
                max-width: 100% !important;
                width: 100% !important;
            }

            .slot.ONE_FOURTH .image img.not-resized {
                max-width: 100% !important;
                width: 100% !important;
            }

            .row-table-body {
                width: 100% !important;
            }

            .product-element-price {
                width: 50% !important;
                margin: 0 !important;
                padding: 10px !important;
            }

            .inner-row-table {
                max-width: 600px;
                width: 100% !important;
            }
        }
    </style>
</head>

<body style="padding: 0px; margin: 0px; font-family: arial, sans-serif; background-repeat: repeat; background-size: auto; background-color: rgb(2, 2, 2);" border="0" background="https://cdn.designer-images.net/yannis_161216101708006.png">
    <table align="center" class="wrapper-table" width="100%" height="100%" border="0" cellspacing="0" cellpadding="0" background="https://cdn.designer-images.net/yannis_161216101708006.png" style="background-repeat: repeat; background-size: auto; background-color: rgb(2, 2, 2);">
        <tbody>
            <tr>
                <td class="wrapper-td" valign="top" align="center" background="https://cdn.designer-images.net/yannis_161216101708006.png" style="background-repeat: repeat; background-size: auto; background-color: rgb(2, 2, 2);">
                    <table border="0" cellspacing="0" cellpadding="0" align="center" class="main-table" width="100%">
                        <tbody>
                            <tr>
                                <td align="center" class="content">
                                    <table data-structure-type="row" data-row-type="FULL" data-row-id="22dc88f8-8a94-5491-b489-5335db10da60" data-row-behavior="NORMAL" data-row-repeat-count="5" data-row-sort-products="Orders" data-row-background-color-wide="transparent" cellpadding="0" cellspacing="0" width="100%" class="newsletter-row row22dc88f8 responsive-row" bgcolor="transparent">
                                        <tbody>
                                            <tr>
                                                <td class="row-td" align="center">
                                                    <table class="inner-row-table" cellpadding="0" cellspacing="0" width="600" valign="top" bgcolor="transparent" style="background-repeat: no-repeat; background-position: initial; border-radius: 0px;">
                                                        <tbody class="row-table-body" style="display: table; width: 600px;">
                                                            <tr>
                                                                <td class="slot slot31dcd85e FULL" data-structure-type="slot" data-slot-type="FULL" width="600" cellpadding="0" cellspacing="0" align="left" valign="top" style="font-weight: normal; max-width: 600px; width: 600px; border-radius: 0px; overflow: visible;">
                                                                    <table class="component spacer-component spacer1ee28c98" data-component-type="spacer" cellspacing="0" cellpadding="0" width="600" align="top" style="background-color: transparent; clear: both; height: 80px; border-width: 0px; border-radius: 0px; border-color: rgb(0, 0, 0); border-style: unset; border-collapse: initial;">
                                                                        <tbody>
                                                                            <tr>
                                                                                <td height="80" style="height: 80px;">
                                                                                    <div style="display: none; font-size: 1px;">&nbsp;</div>
                                                                                </td>
                                                                            </tr>
                                                                        </tbody>
                                                                    </table>
                                                                    <table class="component text-component text-desktop text6ed57cb3" data-component-type="text" cellspacing="0" cellpadding="0" width="600" style="clear: both; background-color: transparent;">
                                                                        <tbody>
                                                                            <tr>
                                                                                <td class="element-td text-element-td" style="overflow-wrap: break-word; word-break: break-word;">
                                                                                    <div class="text_container newsletter-main-content" style="padding: 10px; border-width: 0px; border-color: rgb(0, 0, 0); border-radius: 0px; border-style: unset; color: rgb(0, 0, 0); font-family: Arial, Helvetica, sans-serif, Arial, Helvetica, sans-serif; line-height: 1.3; font-size: 16px;">
                                                                                        <p style="text-align: center; margin: 0px;"><span style="font-size: 28px;"><span style="font-family: &quot;Arial Black&quot;, Gadget, sans-serif, Arial, Helvetica, sans-serif;"><span style="color: rgb(255, 255, 255);">Newsletter subscribed!</span></span></span></p>
                                                                                        <p class="fix-android-mail" style="max-width: 580px; width: 100%; margin: 0px;"></p>
                                                                                    </div>
                                                                                    <div>
                                                                                        <!--[if gte mso 15]><div style="display: 'none'; font-size: 1px; line-height: 1px;">&nbsp;</div><![endif]-->
                                                                                    </div>
                                                                                    <!--[if gte mso 15]><div style="display: none; font-size: 1px; line-height: 1px;">&nbsp;</div><![endif]-->
                                                                                </td>
                                                                            </tr>
                                                                        </tbody>
                                                                    </table>
                                                                    <table class="component image-component image78604e9d" data-component-type="image" data-parent-slot-type="FULL" cellspacing="0" cellpadding="0" width="600" style="clear: both; background-color: transparent;">
                                                                        <tbody>
                                                                            <tr class="newsletter-main-content">
                                                                                <td class="image image-container" align="center" style="line-height: 1px; padding: 0px;"><img src="https://moosendimages.imgix.net/d7156577-f2b1-0e20-f5b2-8d1804d94ca6/b28fae9f8f204241a3afc62aa568346e/whatsapp-image-2022-11-02-at-01.46.04.jpeg?auto=format%2Ccompress&amp;dpr=1&amp;fit=clip&amp;ixjsv=2.2.4&amp;w=593" alt="Email Image" class="newsletter-image " height="auto" width="593" data-resize-width="593" data-resize-height="0" data-original-src="https://cdn.designer-images.net/d7156577-f2b1-0e20-f5b2-8d1804d94ca6/b28fae9f8f204241a3afc62aa568346e/whatsapp-image-2022-11-02-at-01.46.04.jpeg" align="bottom" style="box-sizing: border-box; display: inline-block; border-width: 0px; border-color: rgb(0, 0, 0); border-radius: 0px; border-style: unset;"></td>
                                                                            </tr>
                                                                        </tbody>
                                                                    </table>
                                                                    <table class="component spacer-component spacer3db0fbda" data-component-type="spacer" cellspacing="0" cellpadding="0" width="600" align="top" style="background-color: transparent; clear: both; height: 80px; border-width: 0px; border-radius: 0px; border-color: rgb(0, 0, 0); border-style: unset; border-collapse: initial;">
                                                                        <tbody>
                                                                            <tr>
                                                                                <td height="80" style="height: 80px;">
                                                                                    <div style="display: none; font-size: 1px;">&nbsp;</div>
                                                                                </td>
                                                                            </tr>
                                                                        </tbody>
                                                                    </table>
                                                                    <table class="component text-component text-desktop text8cf30dff" data-component-type="text" cellspacing="0" cellpadding="0" width="600" style="clear: both; background-color: transparent;">
                                                                        <tbody>
                                                                            <tr>
                                                                                <td class="element-td text-element-td" style="overflow-wrap: break-word; word-break: break-word;">
                                                                                    <div class="text_container newsletter-main-content" style="padding: 10px; border-width: 0px; border-color: rgb(0, 0, 0); border-radius: 0px; border-style: unset; color: rgb(0, 0, 0); font-family: Arial, Helvetica, sans-serif, Arial, Helvetica, sans-serif; line-height: 1.3; font-size: 16px;">
                                                                                        <p style="text-align: center; margin: 0px;"><strong style=""><span style="font-family: Arial, Helvetica, sans-serif, Arial, Helvetica, sans-serif;"><span style="font-size: 26px;"><span style="color: rgb(255, 255, 255);">KEEP IN TOUCH WITH US</span></span></span></strong></p>
                                                                                        <p style="text-align: center; margin: 0px;">&nbsp;</p>
                                                                                        <p style="text-align: center; margin: 0px;"><span style="font-size: 12px;"><span style="font-family: Arial, Helvetica, sans-serif, Arial, Helvetica, sans-serif;"><span style="color: rgb(255, 255, 255);">DONATE YOUR VOICE AS AN AUDIO BOOK.</span></span></span></p>
                                                                                        <p class="fix-android-mail" style="max-width: 580px; width: 100%; margin: 0px;"></p>
                                                                                    </div>
                                                                                    <div>
                                                                                        <!--[if gte mso 15]><div style="display: 'none'; font-size: 1px; line-height: 1px;">&nbsp;</div><![endif]-->
                                                                                    </div>
                                                                                </td>
                                                                            </tr>
                                                                        </tbody>
                                                                    </table>
                                                                    <table class="component spacer-component spacer21299ded" data-component-type="spacer" cellspacing="0" cellpadding="0" width="600" align="top" style="background-color: transparent; clear: both; height: 40px; border-width: 0px; border-radius: 0px; border-color: rgb(0, 0, 0); border-style: unset; border-collapse: initial;">
                                                                        <tbody>
                                                                            <tr>
                                                                                <td height="40" style="height: 40px;">
                                                                                    <div style="display: none; font-size: 1px;">&nbsp;</div>
                                                                                </td>
                                                                            </tr>
                                                                        </tbody>
                                                                    </table>
                                                                </td>
                                                            </tr>
                                                        </tbody>
                                                    </table>
                                                </td>
                                            </tr>
                                        </tbody>
                                    </table>
                                    <table data-structure-type="row" data-row-type="FULL" data-row-id="efe7529b-d125-5182-bd0d-77445448a70b" data-row-behavior="NORMAL" data-row-repeat-count="5" data-row-sort-products="Orders" data-row-background-color-wide="transparent" cellpadding="0" cellspacing="0" width="100%" class="newsletter-row rowefe7529b responsive-row" bgcolor="transparent">
                                        <tbody>
                                            <tr>
                                                <td class="row-td" align="center">
                                                    <table class="inner-row-table" cellpadding="0" cellspacing="0" width="600" valign="top" bgcolor="transparent" style="background-repeat: no-repeat; background-position: initial; border-radius: 0px;">
                                                        <tbody class="row-table-body" style="display: table; width: 600px;">
                                                            <tr>
                                                                <td class="slot slot8c1e3b9c FULL" data-structure-type="slot" data-slot-type="FULL" width="600" cellpadding="0" cellspacing="0" align="left" valign="top" style="font-weight: normal; max-width: 600px; width: 600px; border-radius: 0px; overflow: visible;">
                                                                    <table data-component-type="button" class="component button-component button2cd7ed2a" cellspacing="0" cellpadding="0" width="600" border="0" style="width: 600px; vertical-align: top; background-color: transparent; clear: both;">
                                                                        <tbody>
                                                                            <tr class="newsletter-main-content">
                                                                                <td class="element-td" align="center" style="padding: 0px;">
                                                                                    <table class="button-wrapper" cellspacing="0" align="center" border="0" cellpadding="16" style="line-height: normal; vertical-align: baseline; text-align: center; border-collapse: separate; min-width: 10px; background-color: rgb(0, 240, 208); width: auto; border-width: 2px; border-color: rgb(74, 74, 74); border-style: solid;">
                                                                                        <tbody>
                                                                                            <tr>
                                                                                                <td width="100%" align="center" style="padding: 16px;"><a class="newsletter-button-link" href="https://github.com/Audimax-library/audio-library-web-app" style="height: 100%; line-height: normal; display: inline-block; text-align: center; color: rgb(0, 0, 0); font-family: &quot;Bookman Old Style&quot;, serif, Arial, Helvetica, sans-serif; font-style: italic; font-size: 16px; font-weight: bold; width: auto; text-decoration: none !important;" target="_blank"><span class="button" style="color: rgb(0, 0, 0); display: block; min-width: 10px;">AUDIMAX</span></a></td>
                                                                                            </tr>
                                                                                        </tbody>
                                                                                    </table>
                                                                                    <!--[if gte mso 15]><div style="display: none; font-size: 1px; line-height: 1px;">&nbsp;</div><![endif]-->
                                                                                </td>
                                                                            </tr>
                                                                        </tbody>
                                                                    </table>
                                                                    <table class="component spacer-component spacer8ca18742" data-component-type="spacer" cellspacing="0" cellpadding="0" width="600" align="top" style="background-color: transparent; clear: both; height: 80px; border-width: 0px; border-radius: 0px; border-color: rgb(0, 0, 0); border-style: unset; border-collapse: initial;">
                                                                        <tbody>
                                                                            <tr>
                                                                                <td height="80" style="height: 80px;">
                                                                                    <div style="display: none; font-size: 1px;">&nbsp;</div>
                                                                                </td>
                                                                            </tr>
                                                                        </tbody>
                                                                    </table>
                                                                    <table class="component text-component text-desktop textbd5a4dcc" data-component-type="text" cellspacing="0" cellpadding="0" width="600" style="clear: both; background-color: transparent;">
                                                                        <tbody>
                                                                            <tr>
                                                                                <td class="element-td text-element-td" style="overflow-wrap: break-word; word-break: break-word;">
                                                                                    <div class="text_container newsletter-main-content" style="padding: 10px; border-width: 0px; border-color: rgb(0, 0, 0); border-radius: 0px; border-style: unset; color: rgb(0, 0, 0); font-family: Arial, Helvetica, sans-serif, Arial, Helvetica, sans-serif; line-height: 1.3; font-size: 16px;">
                                                                                        <p style="text-align: center; margin: 0px;"><span style="font-size: 16px;"><span style="font-family: Arial, Helvetica, sans-serif, Arial, Helvetica, sans-serif;"><span style="color: rgb(255, 255, 255);">STAY TUNED</span></span></span></p>
                                                                                        <p class="fix-android-mail" style="max-width: 580px; width: 100%; margin: 0px;"></p>
                                                                                    </div>
                                                                                    <div>
                                                                                        <!--[if gte mso 15]><div style="display: 'none'; font-size: 1px; line-height: 1px;">&nbsp;</div><![endif]-->
                                                                                    </div>
                                                                                    <!--[if gte mso 15]><div style="display: none; font-size: 1px; line-height: 1px;">&nbsp;</div><![endif]-->
                                                                                </td>
                                                                            </tr>
                                                                        </tbody>
                                                                    </table>
                                                                    <table class="component spacer-component spacer612472a4" data-component-type="spacer" cellspacing="0" cellpadding="0" width="600" align="top" style="background-color: transparent; clear: both; height: 40px; border-width: 0px; border-radius: 0px; border-color: rgb(0, 0, 0); border-style: unset; border-collapse: initial;">
                                                                        <tbody>
                                                                            <tr>
                                                                                <td height="40" style="height: 40px;">
                                                                                    <div style="display: none; font-size: 1px;">&nbsp;</div>
                                                                                </td>
                                                                            </tr>
                                                                        </tbody>
                                                                    </table>
                                                                    <table class="component social-follow-component socialfollow41ff0f8a" data-component-type="social_follow" cellspacing="0" cellpadding="0" width="600" align="center" data-icon-style="blue" style="clear: both; table-layout: fixed; background-color: transparent;">
                                                                        <tbody>
                                                                            <tr class="newsletter-main-content">
                                                                                <td align="center" style="padding: 0px;">
                                                                                    <table cellspacing="0" cellpadding="0" style="text-align: center;">
                                                                                        <tbody>
                                                                                            <tr class="social-follow-row" style="text-align: center;">
                                                                                                <td><a></a></td>
                                                                                                <td class="social-icon-spacing" width="25" height="10" style="display: inline-block;"></td>
                                                                                                <td class="social-icon-td" style="display: inline-block;"><a data-icon-type="facebook" href="https://www.facebook.com/nuyun.pabasara.5/" class="social_icon facebook" style="display: block; cursor: pointer; text-decoration: none !important;" target="_blank"><img srcset="https://cdn-editor.moosend.com/assets/images/social_icons/social_follow/blue/facebook@3x.png 3x, https://cdn-editor.moosend.com/assets/images/social_icons/social_follow/blue/facebook@2x.png 2x, https://cdn-editor.moosend.com/assets/images/social_icons/social_follow/blue/facebook.png 1x" src="https://cdn-editor.moosend.com/assets/images/social_icons/social_follow/blue/facebook.png" alt="social icon" border="0" style="vertical-align: bottom; display: block;"></a></td>
                                                                                                <td class="social-icon-spacing" width="25" height="10" style="display: inline-block;"></td>
                                                                                                <td class="social-icon-spacing" width="25" height="10" style="display: inline-block;"></td>
                                                                                                <td class="social-icon-td" style="display: inline-block;"><a data-icon-type="twitter" href="https://twitter.com/NKalamullage&quot; class=&quot;social_icon twitter" class="social_icon twitter" style="display: block; cursor: pointer; text-decoration: none !important;" target="_blank"><img srcset="https://cdn-editor.moosend.com/assets/images/social_icons/social_follow/blue/twitter@3x.png 3x, https://cdn-editor.moosend.com/assets/images/social_icons/social_follow/blue/twitter@2x.png 2x, https://cdn-editor.moosend.com/assets/images/social_icons/social_follow/blue/twitter.png 1x" src="https://cdn-editor.moosend.com/assets/images/social_icons/social_follow/blue/twitter.png" alt="social icon" border="0" style="vertical-align: bottom; display: block;"></a></td>
                                                                                                <td class="social-icon-spacing" width="25" height="10" style="display: inline-block;"></td>
                                                                                                <td class="social-icon-spacing" width="25" height="10" style="display: inline-block;"></td>
                                                                                                <td class="social-icon-td" style="display: inline-block;"><a data-icon-type="instagram" href="https://www.instagram.com/nuyun_99/&quot; class=&quot;social_icon instagram" class="social_icon instagram" style="display: block; cursor: pointer; text-decoration: none !important;" target="_blank"><img srcset="https://cdn-editor.moosend.com/assets/images/social_icons/social_follow/blue/instagram@3x.png 3x, https://cdn-editor.moosend.com/assets/images/social_icons/social_follow/blue/instagram@2x.png 2x, https://cdn-editor.moosend.com/assets/images/social_icons/social_follow/blue/instagram.png 1x" src="https://cdn-editor.moosend.com/assets/images/social_icons/social_follow/blue/instagram.png" alt="social icon" border="0" style="vertical-align: bottom; display: block;"></a></td>
                                                                                                <td class="social-icon-spacing" width="25" height="10" style="display: inline-block;"></td>
                                                                                                <td class="social-icon-spacing" width="25" height="10" style="display: inline-block;"></td>
                                                                                                <td class="social-icon-td" style="display: inline-block;"><a data-icon-type="linkedin" href="https://www.linkedin.com/in/nuyun-pabasara-3159841b5/" class="social_icon linkedin" style="display: block; cursor: pointer; text-decoration: none !important;" target="_blank"><img srcset="https://cdn-editor.moosend.com/assets/images/social_icons/social_follow/blue/linkedin@3x.png 3x, https://cdn-editor.moosend.com/assets/images/social_icons/social_follow/blue/linkedin@2x.png 2x, https://cdn-editor.moosend.com/assets/images/social_icons/social_follow/blue/linkedin.png 1x" src="https://cdn-editor.moosend.com/assets/images/social_icons/social_follow/blue/linkedin.png" alt="social icon" border="0" style="vertical-align: bottom; display: block;"></a></td>
                                                                                                <td class="social-icon-spacing" width="25" height="10" style="display: inline-block;"></td>
                                                                                            </tr>
                                                                                        </tbody>
                                                                                    </table>
                                                                                </td>
                                                                            </tr>
                                                                        </tbody>
                                                                    </table>
                                                                    <table class="component spacer-component spacer80184df5" data-component-type="spacer" cellspacing="0" cellpadding="0" width="600" align="top" style="background-color: transparent; clear: both; height: 80px; border-width: 0px; border-radius: 0px; border-color: rgb(0, 0, 0); border-style: unset; border-collapse: initial;">
                                                                        <tbody>
                                                                            <tr>
                                                                                <td height="80" style="height: 80px;">
                                                                                    <div style="display: none; font-size: 1px;">&nbsp;</div>
                                                                                </td>
                                                                            </tr>
                                                                        </tbody>
                                                                    </table>
                                                                </td>
                                                            </tr>
                                                        </tbody>
                                                    </table>
                                                </td>
                                            </tr>
                                        </tbody>
                                    </table>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </td>
            </tr>
        </tbody>
    </table>
</body>

</html>
""",subtype='html')
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, Reciver_email, em.as_string())

