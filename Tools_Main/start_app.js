const { exec } = require('child_process');

exec('C:\\Users\\prisma\\Desktop\\Tools\\Tools_Main\\start_app.bat', (error, stdout, stderr) => {
    if (error) {
        console.error(`Error: ${error.message}`);
        return;
    }
    if (stderr) {
        console.error(`stderr: ${stderr}`);
        return;
    }
    console.log(`stdout: ${stdout}`);
});
