using System;
using System.Diagnostics;
using System.IO;
using System.Windows.Forms;

[assembly: System.Reflection.AssemblyTitle("Remove Music")]
[assembly: System.Reflection.AssemblyProduct("Remove Music")]

internal static class RemoveMusicLauncher
{
    [STAThread]
    private static int Main(string[] args)
    {
        try
        {
            if (args.Length != 1 || !File.Exists(args[0]))
                throw new ArgumentException("Choose one video file from the Send to menu.");

            string root = AppDomain.CurrentDomain.BaseDirectory;
            string pythonw = Path.Combine(root, ".venv", "Scripts", "pythonw.exe");
            string script = Path.Combine(root, "remove_music.py");
            if (!File.Exists(pythonw) || !File.Exists(script))
                throw new FileNotFoundException("The app files are incomplete. Run install.ps1 again.");

            ProcessStartInfo start = new ProcessStartInfo();
            start.FileName = pythonw;
            start.Arguments = "\"" + script + "\" \"" + Path.GetFullPath(args[0]) + "\"";
            start.WorkingDirectory = root;
            start.UseShellExecute = false;
            Process.Start(start);
            return 0;
        }
        catch (Exception error)
        {
            MessageBox.Show(error.Message, "Could not start Remove Music", MessageBoxButtons.OK, MessageBoxIcon.Error);
            return 1;
        }
    }
}
