using System;
using System.IO;
using System.IO.Ports;
using System.Collections.Generic;


// [GENERATED_STRUCT_START]
public struct CanFrame
{
    public int TestInt;
}
// [GENERATED_STRUCT_END]

public class CanSender
{
    // [PORTNAME_START]
    private const string PortName = "COM3";
    // [PORTNAME_END]
    // [BAUDRATE_START]
    private const int BaudRate = 1500000;
    // [BAUDRATE_END]

    public static void Main()
    {
        using (SerialPort serialPort = new SerialPort(PortName, BaudRate))
        {
            try
            {
                serialPort.Open();

                // Testwert zuweisen
                CanFrame myFrame = new CanFrame { TestInt = -1000 };

                // Senden
                SendCanFrame(serialPort, myFrame);

                Console.WriteLine($"Wert {myFrame.TestInt} wurde COBS-kodiert gesendet.");
                Console.WriteLine("Drücke ENTER zum Beenden...");
                Console.ReadLine();
            }
            catch (Exception ex)
            {
                Console.WriteLine("Fehler: " + ex.Message);
                Console.ReadLine();
            }
        }
    }

    public static void SendCanFrame(SerialPort serialPort, CanFrame frame)
    {
        // Schritt 1: Das Struct logisch in Bytes zerlegen
        byte[] payload = SerializeFrame(frame);

        // Schritt 2: COBS-Kodierung (Byte-für-Byte Bearbeitung)
        byte[] encoded = CobsEncode(payload);

        // Schritt 3: Absenden
        serialPort.Write(encoded, 0, encoded.Length);
    }
    // [GENERATED_SERIALIZE_START]
    private static byte[] SerializeFrame(CanFrame frame)
    {
        List<byte> bytes = new List<byte>();
        bytes.AddRange(BitConverter.GetBytes(frame.TestInt));
        return bytes.ToArray();
    }
    // [GENERATED_SERIALIZE_END]
    public static byte[] CobsEncode(byte[] input)
    {
        List<byte> output = new List<byte>();
        output.Add(0);
        int codeIndex = 0;
        byte code = 1;

        foreach (byte b in input)
        {
            if (b == 0)
            {
                output[codeIndex] = code;
                code = 1;
                codeIndex = output.Count;
                output.Add(0);
            }
            else
            {
                output.Add(b);
                code++;
            }
        }
        output[codeIndex] = code;
        output.Add(0x00); // Zero-Terminator
        return output.ToArray();
    }
}