import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

export default function CodeDiffViewer() {
  // Props are globally injected - access them directly
  const filename = props.filename || "Unnamed File";
  const old_text = props.old_text || "";
  const new_text = props.new_text || "";
  const language = props.language || "typescript";
  
  const [view, setView] = useState("unified"); // unified, split, original, modified
  
  // Improved diff algorithm
  const computeDiff = (oldText, newText) => {
    const oldLines = oldText.split('\n');
    const newLines = newText.split('\n');
    const changes = [];
    
    // Create a matrix to store the length of LCS
    const lcsMatrix = Array(oldLines.length + 1).fill().map(() => 
      Array(newLines.length + 1).fill(0)
    );
    
    // Fill the LCS matrix
    for (let i = 1; i <= oldLines.length; i++) {
      for (let j = 1; j <= newLines.length; j++) {
        if (oldLines[i-1] === newLines[j-1]) {
          lcsMatrix[i][j] = lcsMatrix[i-1][j-1] + 1;
        } else {
          lcsMatrix[i][j] = Math.max(lcsMatrix[i-1][j], lcsMatrix[i][j-1]);
        }
      }
    }
    
    // Backtrack to find the diff
    let i = oldLines.length;
    let j = newLines.length;
    
    const diff = [];
    
    while (i > 0 || j > 0) {
      if (i > 0 && j > 0 && oldLines[i-1] === newLines[j-1]) {
        // Lines match - keep
        diff.unshift({
          type: 'normal',
          content: oldLines[i-1],
          oldLineNumber: i,
          lineNumber: j
        });
        i--;
        j--;
      } else if (j > 0 && (i === 0 || lcsMatrix[i][j-1] >= lcsMatrix[i-1][j])) {
        // Addition
        diff.unshift({
          type: 'add',
          content: newLines[j-1],
          oldLineNumber: null,
          lineNumber: j
        });
        j--;
      } else if (i > 0 && (j === 0 || lcsMatrix[i][j-1] < lcsMatrix[i-1][j])) {
        // Deletion
        diff.unshift({
          type: 'delete',
          content: oldLines[i-1],
          oldLineNumber: i,
          lineNumber: null
        });
        i--;
      }
    }
    
    return diff;
  };
  
  const parsedDiff = {
    filename: filename,
    changes: computeDiff(old_text, new_text)
  };
  
  // Simple syntax highlighting for common code elements
  const highlightSyntax = (text) => {
    return text
      .replace(/import\s+/g, '<span class="text-purple-600 dark:text-purple-400">import </span>')
      .replace(/export\s+/g, '<span class="text-purple-600 dark:text-purple-400">export </span>')
      .replace(/from\s+/g, '<span class="text-purple-600 dark:text-purple-400">from </span>')
      .replace(/const\s+/g, '<span class="text-blue-600 dark:text-blue-400">const </span>')
      .replace(/let\s+/g, '<span class="text-blue-600 dark:text-blue-400">let </span>')
      .replace(/function\s+/g, '<span class="text-blue-600 dark:text-blue-400">function </span>')
      .replace(/return\s+/g, '<span class="text-purple-600 dark:text-purple-400">return </span>')
      .replace(/if\s*\(/g, '<span class="text-purple-600 dark:text-purple-400">if</span>(')
      .replace(/else\s*/g, '<span class="text-purple-600 dark:text-purple-400">else</span> ')
      .replace(/await\s+/g, '<span class="text-purple-600 dark:text-purple-400">await </span>')
      .replace(/async\s+/g, '<span class="text-purple-600 dark:text-purple-400">async </span>')
      .replace(/(["'])(?:\\.|[^\\])*?\1/g, '<span class="text-green-600 dark:text-green-400">$&</span>')
      .replace(/\/\/.*$/gm, '<span class="text-gray-500">$&</span>');
  };
  
  // Get styling for different change types
  const getChangeStyle = (type) => {
    switch(type) {
      case 'add':
      case 'added':
      case 'insertion':
        return 'bg-green-100 dark:bg-green-900/30 border-l-4 border-green-500';
      case 'delete':
      case 'deleted':
      case 'removed':
        return 'bg-red-100 dark:bg-red-900/30 border-l-4 border-red-500';
      case 'modified':
      case 'changed':
        return 'bg-yellow-100 dark:bg-yellow-900/30 border-l-4 border-yellow-500';
      default:
        return '';
    }
  };
  
  // Get symbol for change type
  const getChangeSymbol = (type) => {
    switch(type) {
      case 'add':
      case 'added':
      case 'insertion':
        return <span className="text-green-600 dark:text-green-400 font-bold">+</span>;
      case 'delete':
      case 'deleted':
      case 'removed':
        return <span className="text-red-600 dark:text-red-400 font-bold">-</span>;
      case 'modified':
      case 'changed':
        return <span className="text-yellow-600 dark:text-yellow-400 font-bold">~</span>;
      default:
        return ' ';
    }
  };

  // Render unified diff view
  const renderUnifiedDiff = () => {
    return parsedDiff.changes.map((change, index) => (
      <div key={index} className={`px-2 whitespace-pre font-mono ${getChangeStyle(change.type)}`}>
        <span className="inline-block w-6 text-center text-gray-500 mr-2">
          {getChangeSymbol(change.type)}
        </span>
        <span className="inline-block w-8 text-right text-gray-500 mr-4">
          {change.type === 'delete' ? change.oldLineNumber : change.lineNumber || ''}
        </span>
        <span 
          className={getTextColorClass(change.type)}
          dangerouslySetInnerHTML={{ __html: highlightSyntax(change.content || '') }} 
        />
      </div>
    ));
  };
  
  // Render a version (original or modified)
  const renderVersion = (text, title) => {
    const lines = text.split('\n');
    return (
      <div>
        <div className="text-sm font-medium mb-2">{title}</div>
        <div className="bg-gray-50 dark:bg-gray-900 rounded-md p-2 text-sm font-mono overflow-auto max-h-96">
          {lines.map((line, index) => (
            <div key={index} className="px-2 whitespace-pre">
              <span className="inline-block w-8 text-right text-gray-500 mr-4">
                {index + 1}
              </span>
              <span dangerouslySetInnerHTML={{ __html: highlightSyntax(line) }} />
            </div>
          ))}
        </div>
      </div>
    );
  };
  
  // Calculate statistics
  const stats = {
    additions: parsedDiff.changes.filter(c => c.type === 'add').length,
    deletions: parsedDiff.changes.filter(c => c.type === 'delete').length,
    modifications: 0 // We're not detecting modifications with this simple algorithm
  };

  // Get text color class for different change types
  const getTextColorClass = (type) => {
    switch(type) {
      case 'add':
      case 'added':
      case 'insertion':
        return 'text-green-800 dark:text-green-300 font-medium';
      case 'delete':
      case 'deleted':
      case 'removed':
        return 'text-red-800 dark:text-red-300 font-medium';
      case 'modified':
      case 'changed':
        return 'text-yellow-800 dark:text-yellow-300 font-medium';
      default:
        return '';
    }
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <div className="flex justify-between items-center">
          <div className="flex items-center space-x-2">
            <CardTitle className="text-lg font-medium">{parsedDiff.filename}</CardTitle>
            <Badge variant="outline" className="text-green-600">
              +{stats.additions}
            </Badge>
            <Badge variant="outline" className="text-red-600">
              -{stats.deletions}
            </Badge>
          </div>
          <div className="flex space-x-2">
            <Button 
              variant={view === "unified" ? "default" : "outline"}
              size="sm"
              onClick={() => setView("unified")}
            >
              Unified
            </Button>
            <Button 
              variant={view === "split" ? "default" : "outline"}
              size="sm"
              onClick={() => setView("split")}
            >
              Split
            </Button>
            <Button 
              variant={view === "original" ? "default" : "outline"}
              size="sm"
              onClick={() => setView("original")}
            >
              Original
            </Button>
            <Button 
              variant={view === "modified" ? "default" : "outline"}
              size="sm"
              onClick={() => setView("modified")}
            >
              Modified
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {view === "unified" && (
          <div className="bg-gray-50 dark:bg-gray-900 rounded-md p-2 text-sm overflow-auto max-h-96">
            <div className="px-2 whitespace-pre font-mono mb-2 text-gray-500 text-xs">
              <span className="inline-block w-6 text-center mr-2"></span>
              <span className="inline-block w-8 text-right mr-4">Line</span>
              <span>Code</span>
            </div>
            {renderUnifiedDiff()}
          </div>
        )}
        
        {view === "split" && (
          <div className="grid grid-cols-2 gap-4">
            {renderVersion(old_text, "Original")}
            {renderVersion(new_text, "Modified")}
          </div>
        )}
        
        {view === "original" && renderVersion(old_text, "Original")}
        {view === "modified" && renderVersion(new_text, "Modified")}
        
        <div className="mt-4 flex justify-center space-x-4">
          <div className="flex items-center">
            <div className="w-4 h-4 rounded bg-green-100 dark:bg-green-900/30 border border-green-500 mr-2"></div>
            <span className="text-sm">Added</span>
          </div>
          <div className="flex items-center">
            <div className="w-4 h-4 rounded bg-red-100 dark:bg-red-900/30 border border-red-500 mr-2"></div>
            <span className="text-sm">Removed</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}